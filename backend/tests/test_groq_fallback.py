from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.chat import ChatRequest
from models.response_validation import ResponseValidationResult
from services.chat_service import ChatService
from services.llm.base_provider import LLMGenerationResult
from services.llm.gemini_provider import GeminiProviderError
from services.llm.groq_provider import GroqProvider, GroqProviderError
from services.llm.provider_coordinator import ProviderFallbackCoordinator


class GroqProviderTests(unittest.TestCase):
    def make_provider(self, outcomes):
        remaining = list(outcomes)
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            outcome = remaining.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

        provider = GroqProvider(api_key="test-secret", model_name="groq-test")
        provider.client.close()
        provider.client = httpx.Client(transport=httpx.MockTransport(handler))
        return provider, requests

    def test_success_sends_openai_compatible_request_and_usage_metadata(self):
        provider, requests = self.make_provider([httpx.Response(200, json={
            "choices": [{"finish_reason": "stop", "message": {"content": " answer "}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        })])
        try:
            result = provider.generate_with_metadata("private prompt", temperature=0.4, max_tokens=120)
        finally:
            provider.close()
        request = requests[0]
        self.assertEqual(str(request.url), GroqProvider.ENDPOINT)
        self.assertEqual(request.headers["authorization"], "Bearer test-secret")
        self.assertEqual(request.read() and __import__("json").loads(request.content)["messages"][0]["content"], "private prompt")
        self.assertEqual(result, LLMGenerationResult("answer", "STOP", True, 11, 7, None, 18))

    def test_incomplete_response_preserves_partial_text_and_usage(self):
        provider, _ = self.make_provider([httpx.Response(200, json={
            "choices": [{"finish_reason": "length", "message": {"content": "partial"}}],
            "usage": {"prompt_tokens": 4, "completion_tokens": 8, "total_tokens": 12},
        })])
        try:
            result = provider.generate_with_metadata("prompt")
        finally:
            provider.close()
        self.assertFalse(result.completed)
        self.assertEqual(result.text, "partial")
        self.assertEqual(result.finish_reason, "LENGTH")
        self.assertEqual(result.total_token_count, 12)

    def test_malformed_and_empty_response_are_rejected(self):
        for response in (httpx.Response(200, json={"bad": True}), httpx.Response(200, json={
            "choices": [{"finish_reason": "stop", "message": {"content": " "}}],
        })):
            provider, _ = self.make_provider([response])
            try:
                with self.assertRaises(GroqProviderError) as caught:
                    provider.generate_with_metadata("prompt")
                self.assertEqual(caught.exception.category, "unexpected_api_response")
            finally:
                provider.close()

    def test_provider_failure_does_not_log_key_or_prompt(self):
        provider, _ = self.make_provider([httpx.Response(401)])
        try:
            with self.assertLogs("services.llm.groq_provider", level="WARNING") as captured:
                with self.assertRaises(GroqProviderError):
                    provider.generate_with_metadata("PRIVATE_PROMPT")
        finally:
            provider.close()
        logs = "\n".join(captured.output)
        self.assertNotIn("test-secret", logs)
        self.assertNotIn("PRIVATE_PROMPT", logs)


class StubProvider:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def generate_with_metadata(self, prompt, *, temperature=0.2, max_tokens=1500):
        self.calls.append((prompt, temperature, max_tokens))
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome


class ProviderFallbackTests(unittest.TestCase):
    def test_gemini_success_does_not_call_groq(self):
        primary = StubProvider(LLMGenerationResult("answer", "STOP", True))
        fallback = StubProvider(LLMGenerationResult("groq", "STOP", True))
        coordinator = ProviderFallbackCoordinator(primary, fallback)
        result = coordinator.generate_with_metadata("same prompt")
        self.assertEqual(result.text, "answer")
        self.assertEqual(len(primary.calls), 1)
        self.assertEqual(fallback.calls, [])

    def test_quota_5xx_and_timeout_fall_back_with_identical_prompt_and_parameters(self):
        failures = (
            GeminiProviderError("rate_limited", "quota", 429),
            GeminiProviderError("temporary_service_unavailable", "unavailable", 503),
            GeminiProviderError("timeout", "timeout"),
        )
        for failure in failures:
            with self.subTest(failure=failure.category):
                primary = StubProvider(failure)
                fallback = StubProvider(LLMGenerationResult("fallback", "STOP", True))
                result = ProviderFallbackCoordinator(primary, fallback).generate_with_metadata(
                    "full conversation prompt", temperature=0.6, max_tokens=99,
                )
                self.assertEqual(result.text, "fallback")
                self.assertEqual(primary.calls, [("full conversation prompt", 0.6, 99)])
                self.assertEqual(fallback.calls, primary.calls)

    def test_401_400_404_do_not_fall_back(self):
        for category, status in (("invalid_api_key", 401), ("invalid_request", 400), ("model_unavailable", 404)):
            with self.subTest(status=status):
                primary = StubProvider(GeminiProviderError(category, "failure", status))
                fallback = StubProvider(LLMGenerationResult("unused", "STOP", True))
                with self.assertRaises(GeminiProviderError):
                    ProviderFallbackCoordinator(primary, fallback).generate_with_metadata("prompt")
                self.assertEqual(fallback.calls, [])

    def test_groq_failure_is_propagated(self):
        primary = StubProvider(GeminiProviderError("rate_limited", "quota", 429))
        failure = GroqProviderError("temporary_service_unavailable", "Groq unavailable", 503)
        fallback = StubProvider(failure)
        with self.assertRaises(GroqProviderError):
            ProviderFallbackCoordinator(primary, fallback).generate_with_metadata("prompt")

    def test_gemini_429_followed_by_groq_413_preserves_request_size_failure(self):
        primary = StubProvider(GeminiProviderError("rate_limited", "quota", 429))
        fallback = StubProvider(GroqProviderError(
            "request_too_large",
            "The Groq request was too large (HTTP 413).",
            413,
        ))

        with self.assertRaises(GroqProviderError) as caught:
            ProviderFallbackCoordinator(primary, fallback).generate_with_metadata("bounded prompt")

        self.assertEqual(caught.exception.category, "request_too_large")
        self.assertEqual(caught.exception.status_code, 413)
        self.assertEqual(fallback.calls, [("bounded prompt", 0.2, 1500)])

    def test_no_fallback_provider_preserves_primary_error(self):
        primary = StubProvider(GeminiProviderError("rate_limited", "quota", 429))
        with self.assertRaises(GeminiProviderError):
            ProviderFallbackCoordinator(primary).generate_with_metadata("prompt")


class PassingValidator:
    def validate(self, response, *args, **kwargs):
        return ResponseValidationResult(
            passed=True, overall_score=0.9, word_count=10, hallucination_risk=0.0,
            followup_continuity=1.0, category_scores={},
        )


class FallbackCacheTests(unittest.TestCase):
    def test_successful_fallback_uses_existing_chat_pipeline_and_cache(self):
        primary = StubProvider(GeminiProviderError("rate_limited", "quota", 429))
        fallback = StubProvider(LLMGenerationResult("grounded response", "STOP", True))
        service = ChatService(provider=ProviderFallbackCoordinator(primary, fallback))
        service.response_validator = PassingValidator()
        request = ChatRequest(question="Explain Atlas", analysis={"repository": {"name": "atlas"}})
        first = service.generate_answer(request)
        second = service.generate_answer(request)
        self.assertEqual(first.answer, "grounded response")
        self.assertEqual(second.answer, first.answer)
        self.assertEqual(len(primary.calls), 1)
        self.assertEqual(len(fallback.calls), 1)
