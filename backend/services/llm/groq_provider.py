from __future__ import annotations

import logging
from typing import Any

import httpx

from core.config import settings
from services.llm.base_provider import LLMGenerationResult, LLMProvider


class GroqProviderError(RuntimeError):
    """Safe, classified Groq failure without request or credential data."""

    def __init__(self, category: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.category = category
        self.status_code = status_code


class GroqProvider(LLMProvider):
    ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model_name = model_name or settings.GROQ_MODEL
        self.logger = logging.getLogger(__name__)
        self.client = httpx.Client(timeout=httpx.Timeout(120.0))

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1500) -> str:
        result = self.generate_with_metadata(prompt, temperature=temperature, max_tokens=max_tokens)
        if not result.completed:
            raise GroqProviderError("incomplete_generation", "Groq generation did not complete.")
        return result.text

    def generate_with_metadata(
        self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1500
    ) -> LLMGenerationResult:
        if not self.api_key:
            raise GroqProviderError("missing_api_key", "Groq is not configured.")
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            response = self.client.post(
                self.ENDPOINT,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        except httpx.TimeoutException as exc:
            self.logger.warning("Groq request timed out model=%s", self.model_name)
            raise GroqProviderError("timeout", "The AI provider did not respond in time.") from exc
        except httpx.RequestError as exc:
            self.logger.warning("Groq network failure model=%s error_type=%s", self.model_name, type(exc).__name__)
            raise GroqProviderError("network_failure", "A network failure prevented contacting Groq.") from exc

        if response.status_code >= 400:
            category, message = self._classify_status(response.status_code)
            self.logger.warning("Groq HTTP failure model=%s status_code=%d", self.model_name, response.status_code)
            raise GroqProviderError(category, message, response.status_code)
        try:
            data = response.json()
        except (ValueError, TypeError) as exc:
            raise GroqProviderError("unexpected_api_response", "Groq returned a malformed API response.", response.status_code) from exc
        choices = data.get("choices") if isinstance(data, dict) else None
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise GroqProviderError("unexpected_api_response", "Groq returned no valid completion choice.", response.status_code)
        choice = choices[0]
        message = choice.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise GroqProviderError("unexpected_api_response", "Groq returned an empty or malformed response.", response.status_code)
        raw_reason = choice.get("finish_reason")
        finish_reason = raw_reason.strip().upper() if isinstance(raw_reason, str) and raw_reason.strip() else "UNKNOWN"
        usage = data.get("usage") if isinstance(data, dict) else None
        result = LLMGenerationResult(
            text=text.strip(),
            finish_reason=finish_reason,
            completed=finish_reason == "STOP",
            prompt_token_count=self._token_count(usage, "prompt_tokens"),
            candidates_token_count=self._token_count(usage, "completion_tokens"),
            total_token_count=self._token_count(usage, "total_tokens"),
        )
        log = self.logger.info if result.completed else self.logger.warning
        log("Groq generation metadata model=%s finish_reason=%s prompt_token_count=%s candidates_token_count=%s total_token_count=%s completed=%s output_characters=%d", self.model_name, result.finish_reason, result.prompt_token_count, result.candidates_token_count, result.total_token_count, result.completed, len(result.text))
        return result

    @staticmethod
    def _token_count(usage: Any, field: str) -> int | None:
        if not isinstance(usage, dict):
            return None
        value = usage.get(field)
        return value if type(value) is int and value >= 0 else None

    @staticmethod
    def _classify_status(status_code: int) -> tuple[str, str]:
        if status_code == 400:
            return "invalid_request", "Groq rejected the request as invalid (HTTP 400)."
        if status_code == 401:
            return "invalid_api_key", "The Groq API key was rejected (HTTP 401)."
        if status_code == 403:
            return "permission_denied", "The Groq API denied access (HTTP 403)."
        if status_code == 404:
            return "model_unavailable", "The configured Groq model or endpoint was not found (HTTP 404)."
        if status_code == 429:
            return "rate_limited", "The Groq API quota or rate limit has been exceeded (HTTP 429)."
        if status_code >= 500:
            return "temporary_service_unavailable", f"The Groq service is temporarily unavailable (HTTP {status_code})."
        return "provider_http_error", f"The Groq API returned an unexpected HTTP status ({status_code})."

    def close(self) -> None:
        self.client.close()
