import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.llm.base_provider import LLMGenerationResult
from services.llm.gemini_provider import GeminiProvider, GeminiProviderError


class GeminiProviderTests(unittest.TestCase):
    def make_provider(self, outcomes):
        remaining = list(outcomes)
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            outcome = remaining.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

        provider = GeminiProvider(api_key="test-secret", model_name="gemini-test")
        provider.client.close()
        provider.client = httpx.Client(transport=httpx.MockTransport(handler))
        return provider, requests

    def test_successful_request_uses_header_and_extracts_text(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "answer"}]}}]})
        ])
        try:
            answer = provider.generate("private prompt", temperature=0.4, max_tokens=120)
            self.assertEqual(answer, "answer")
            self.assertEqual(len(requests), 1)
            self.assertEqual(requests[0].headers["x-goog-api-key"], "test-secret")
            self.assertNotIn("key=", str(requests[0].url))
            self.assertIn(b"private prompt", requests[0].content)
        finally:
            provider.close()

    def test_503_retries_then_succeeds_with_exponential_backoff(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(503),
            httpx.Response(503),
            httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "recovered"}]}}]}),
        ])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                answer = provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(answer, "recovered")
        self.assertEqual(len(requests), 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_503_stops_after_three_retries(self) -> None:
        provider, requests = self.make_provider([httpx.Response(503) for _ in range(4)])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(len(requests), 4)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2, 4])
        self.assertEqual(caught.exception.category, "temporary_service_unavailable")
        self.assertEqual(caught.exception.status_code, 503)

    def test_429_is_classified_immediately_as_rate_limited(self) -> None:
        provider, requests = self.make_provider([httpx.Response(429) for _ in range(4)])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(len(requests), 1)
        sleep.assert_not_called()
        self.assertEqual(caught.exception.category, "rate_limited")
        self.assertEqual(caught.exception.status_code, 429)

    def test_429_is_not_retried_before_quota_fallback(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(429),
            httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "ok"}]}}]}),
        ])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError):
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(len(requests), 1)
        sleep.assert_not_called()

    def test_429_after_transient_failure_is_not_retried(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(503),
            httpx.Response(429),
            httpx.Response(200, json={"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "ok"}]}}]}),
        ])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(caught.exception.category, "rate_limited")
        self.assertEqual(len(requests), 2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1])

    def test_500_is_retried_then_classified(self) -> None:
        provider, requests = self.make_provider([httpx.Response(500) for _ in range(4)])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(len(requests), 4)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2, 4])
        self.assertEqual(caught.exception.status_code, 500)

    def test_timeout_is_classified_without_retry(self) -> None:
        provider, requests = self.make_provider([httpx.ReadTimeout("slow")])
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(len(requests), 1)
        self.assertEqual(caught.exception.category, "timeout")

    def test_network_failure_is_classified_without_retry(self) -> None:
        provider, requests = self.make_provider([httpx.ConnectError("network")])
        try:
            with self.assertLogs("services.llm.gemini_provider", level="ERROR") as captured:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(len(requests), 1)
        self.assertEqual(caught.exception.category, "network_failure")
        self.assertIn(
            "model=gemini-test retry_number=0 error_type=ConnectError",
            "\n".join(captured.output),
        )

    def test_invalid_api_key_is_not_retried(self) -> None:
        provider, requests = self.make_provider([httpx.Response(401)])
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(len(requests), 1)
        self.assertEqual(caught.exception.category, "invalid_api_key")
        self.assertEqual(caught.exception.status_code, 401)

    def test_bad_request_forbidden_and_not_found_are_not_retried(self) -> None:
        for status, expected_category in ((400, "invalid_request"), (403, "permission_denied"), (404, "model_unavailable")):
            provider, requests = self.make_provider([httpx.Response(status)])
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
            self.assertEqual(len(requests), 1)
            self.assertEqual(caught.exception.category, expected_category)

    def test_missing_key_and_malformed_response_are_classified(self) -> None:
        missing_key = GeminiProvider(api_key=None, model_name="gemini-test")
        missing_key.api_key = None
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                missing_key.generate("prompt")
            self.assertEqual(caught.exception.category, "missing_api_key")
        finally:
            missing_key.close()

        provider, requests = self.make_provider([httpx.Response(200, json={"unexpected": True})])
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(len(requests), 1)
        self.assertEqual(caught.exception.category, "unexpected_api_response")

        malformed_provider, malformed_requests = self.make_provider([
            httpx.Response(200, json={"candidates": [None]})
        ])
        try:
            with self.assertRaises(GeminiProviderError) as malformed_caught:
                malformed_provider.generate("prompt")
        finally:
            malformed_provider.close()
        self.assertEqual(len(malformed_requests), 1)
        self.assertEqual(malformed_caught.exception.category, "unexpected_api_response")

    def test_generation_metadata_distinguishes_stop_from_max_tokens(self) -> None:
        completed, _ = self.make_provider([
            httpx.Response(200, json={
                "candidates": [{
                    "finishReason": "STOP",
                    "content": {"parts": [{"text": "complete answer"}]},
                }],
                "usageMetadata": {
                    "promptTokenCount": 11,
                    "candidatesTokenCount": 7,
                    "thoughtsTokenCount": 2,
                    "totalTokenCount": 20,
                },
            }),
        ])
        try:
            result = completed.generate_with_metadata("prompt")
        finally:
            completed.close()
        self.assertEqual(result.text, "complete answer")
        self.assertEqual(result.finish_reason, "STOP")
        self.assertTrue(result.completed)
        self.assertEqual(result.prompt_token_count, 11)
        self.assertEqual(result.candidates_token_count, 7)
        self.assertEqual(result.thoughts_token_count, 2)
        self.assertEqual(result.total_token_count, 20)

        truncated, _ = self.make_provider([
            httpx.Response(200, json={
                "candidates": [{
                    "finishReason": "MAX_TOKENS",
                    "content": {"parts": [{"text": "partial answer"}]},
                }],
                "usageMetadata": {
                    "promptTokenCount": 13,
                    "candidatesTokenCount": 90,
                    "thoughtsTokenCount": 4,
                    "totalTokenCount": 107,
                },
            }),
        ])
        try:
            with self.assertLogs("services.llm.gemini_provider", level="WARNING") as captured:
                result = truncated.generate_with_metadata("sensitive prompt")
        finally:
            truncated.close()
        self.assertEqual(result.text, "partial answer")
        self.assertEqual(result.finish_reason, "MAX_TOKENS")
        self.assertFalse(result.completed)
        self.assertEqual(result.prompt_token_count, 13)
        self.assertEqual(result.candidates_token_count, 90)
        self.assertEqual(result.thoughts_token_count, 4)
        self.assertEqual(result.total_token_count, 107)
        log_text = "\n".join(captured.output)
        self.assertIn("finish_reason=MAX_TOKENS", log_text)
        self.assertIn("prompt_token_count=13", log_text)
        self.assertIn("candidates_token_count=90", log_text)
        self.assertIn("thoughts_token_count=4", log_text)
        self.assertIn("total_token_count=107", log_text)
        self.assertNotIn("sensitive prompt", log_text)

    def test_usage_metadata_and_individual_token_fields_are_optional(self) -> None:
        for body, expected in (
            (
                {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "answer"}]},
                    }],
                },
                (None, None, None, None),
            ),
            (
                {
                    "candidates": [{
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "answer"}]},
                    }],
                    "usageMetadata": {
                        "promptTokenCount": 9,
                        "totalTokenCount": 12,
                    },
                },
                (9, None, None, 12),
            ),
        ):
            provider, _ = self.make_provider([httpx.Response(200, json=body)])
            try:
                result = provider.generate_with_metadata("prompt")
            finally:
                provider.close()
            self.assertEqual(
                (
                    result.prompt_token_count,
                    result.candidates_token_count,
                    result.thoughts_token_count,
                    result.total_token_count,
                ),
                expected,
            )

    def test_result_constructor_and_generate_remain_backward_compatible(self) -> None:
        legacy_result = LLMGenerationResult("answer", "STOP", True)
        self.assertEqual(legacy_result.prompt_token_count, None)
        self.assertEqual(legacy_result.candidates_token_count, None)
        self.assertEqual(legacy_result.thoughts_token_count, None)
        self.assertEqual(legacy_result.total_token_count, None)

        provider, _ = self.make_provider([
            httpx.Response(200, json={
                "candidates": [{
                    "finishReason": "STOP",
                    "content": {"parts": [{"text": "answer"}]},
                }],
                "usageMetadata": {
                    "promptTokenCount": 11,
                    "candidatesTokenCount": 7,
                    "thoughtsTokenCount": 2,
                    "totalTokenCount": 20,
                },
            }),
        ])
        try:
            answer = provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(answer, "answer")
        self.assertIsInstance(answer, str)

    def test_generate_does_not_return_non_normal_termination_as_success(self) -> None:
        provider, _ = self.make_provider([
            httpx.Response(200, json={
                "candidates": [{
                    "finishReason": "MAX_TOKENS",
                    "content": {"parts": [{"text": "partial answer"}]},
                }],
            }),
        ])
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(caught.exception.category, "incomplete_generation")
        self.assertIn("MAX_TOKENS", str(caught.exception))

    def test_other_termination_and_missing_finish_reason_are_not_complete(self) -> None:
        for candidate, expected_reason in (
            ({"finishReason": "SAFETY", "content": {"parts": []}}, "SAFETY"),
            ({"content": {"parts": [{"text": "unknown termination"}]}}, "UNKNOWN"),
        ):
            provider, _ = self.make_provider([
                httpx.Response(200, json={"candidates": [candidate]}),
            ])
            try:
                result = provider.generate_with_metadata("prompt")
            finally:
                provider.close()
            self.assertEqual(result.finish_reason, expected_reason)
            self.assertFalse(result.completed)

    def test_unknown_finish_reason_logs_adjacent_token_fields_separately(self) -> None:
        provider, _ = self.make_provider([
            httpx.Response(200, json={
                "candidates": [{
                    "content": {"parts": [{"text": "answer with unknown finish reason"}]},
                }],
            }),
        ])
        try:
            with self.assertLogs("services.llm.gemini_provider", level="WARNING") as captured:
                provider.generate_with_metadata("prompt")
        finally:
            provider.close()

        logs = "\n".join(captured.output)
        self.assertIn(
            "finish_reason=UNKNOWN prompt_token_count=None candidates_token_count=None "
            "thoughts_token_count=None total_token_count=None configured_max_output_tokens=1500",
            logs,
        )

    def test_empty_candidates_are_classified_as_malformed_response(self) -> None:
        provider, _ = self.make_provider([
            httpx.Response(200, json={"candidates": []}),
        ])
        try:
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate_with_metadata("prompt")
        finally:
            provider.close()
        self.assertEqual(caught.exception.category, "unexpected_api_response")

    def test_prompt_and_api_key_are_not_logged(self) -> None:
        provider, _ = self.make_provider([httpx.Response(200, json={
            "candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": "ok"}]}}],
            "usageMetadata": {
                "promptTokenCount": 11,
                "candidatesTokenCount": 7,
                "thoughtsTokenCount": 2,
                "totalTokenCount": 20,
            },
        })])
        logger = "services.llm.gemini_provider"
        try:
            with self.assertLogs(logger, level="INFO") as captured:
                provider.generate("SENSITIVE_PROMPT_SENTINEL", max_tokens=77)
            logs = "\n".join(captured.output)
        finally:
            provider.close()
        self.assertNotIn("SENSITIVE_PROMPT_SENTINEL", logs)
        self.assertNotIn("test-secret", logs)
        self.assertIn("model=gemini-test", logs)
        self.assertIn("finish_reason=STOP", logs)
        self.assertIn("prompt_token_count=11", logs)
        self.assertIn("candidates_token_count=7", logs)
        self.assertIn("thoughts_token_count=2", logs)
        self.assertIn("total_token_count=20", logs)
        self.assertIn("total_token_count=20 configured_max_output_tokens=77", logs)
        self.assertIn("configured_max_output_tokens=77", logs)
        self.assertIn(
            "completed=True status_code=200 retry_number=0 output_characters=2",
            logs,
        )


if __name__ == "__main__":
    unittest.main()
