import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
            httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "answer"}]}}]})
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
            httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "recovered"}]}}]}),
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

    def test_429_is_retried_then_classified_as_rate_limited(self) -> None:
        provider, requests = self.make_provider([httpx.Response(429) for _ in range(4)])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                with self.assertRaises(GeminiProviderError) as caught:
                    provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(len(requests), 2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1])
        self.assertEqual(caught.exception.category, "rate_limited")
        self.assertEqual(caught.exception.status_code, 429)

    def test_429_retries_only_once_then_succeeds(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(429),
            httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}),
        ])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                answer = provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(answer, "ok")
        self.assertEqual(len(requests), 2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1])

    def test_429_keeps_its_retry_after_a_prior_transient_failure(self) -> None:
        provider, requests = self.make_provider([
            httpx.Response(503),
            httpx.Response(429),
            httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}),
        ])
        with patch("services.llm.gemini_provider.time.sleep") as sleep:
            try:
                answer = provider.generate("prompt")
            finally:
                provider.close()
        self.assertEqual(answer, "ok")
        self.assertEqual(len(requests), 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

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
            with self.assertRaises(GeminiProviderError) as caught:
                provider.generate("prompt")
        finally:
            provider.close()
        self.assertEqual(len(requests), 1)
        self.assertEqual(caught.exception.category, "network_failure")

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

    def test_prompt_and_api_key_are_not_logged(self) -> None:
        provider, _ = self.make_provider([httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})])
        logger = "services.llm.gemini_provider"
        try:
            with self.assertLogs(logger, level="INFO") as captured:
                provider.generate("SENSITIVE_PROMPT_SENTINEL")
            logs = "\n".join(captured.output)
        finally:
            provider.close()
        self.assertNotIn("SENSITIVE_PROMPT_SENTINEL", logs)
        self.assertNotIn("test-secret", logs)


if __name__ == "__main__":
    unittest.main()
