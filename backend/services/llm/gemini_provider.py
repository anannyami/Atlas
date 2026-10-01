from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from core.config import settings
from services.llm.base_provider import LLMProvider


class GeminiProviderError(RuntimeError):
    """Safe, classified provider failure without request or credential data."""

    def __init__(self, category: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.category = category
        self.status_code = status_code


class GeminiProvider(LLMProvider):
    RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
    RETRY_DELAYS_SECONDS = (1, 2, 4)

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.MODEL_NAME
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.endpoint = f"{self.base_url}/{self.model_name}:generateContent"
        self.logger = logging.getLogger(__name__)
        self.client = httpx.Client(timeout=httpx.Timeout(120.0))

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        if not self.api_key:
            raise GeminiProviderError("missing_api_key", "Gemini is not configured.")

        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        prompt_length = len(prompt)
        prompt_word_count = len(prompt.split())

        retry_count = 0
        rate_limit_retries = 0
        for attempt in range(len(self.RETRY_DELAYS_SECONDS) + 1):
            retry_number = attempt
            self.logger.info(
                "Gemini request model=%s endpoint=%s temperature=%s max_tokens=%d "
                "prompt_length=%d prompt_word_count=%d retry_number=%d",
                self.model_name,
                self.endpoint,
                temperature,
                max_tokens,
                prompt_length,
                prompt_word_count,
                retry_number,
            )

            try:
                response = self.client.post(
                    self.endpoint,
                    json=payload,
                    headers={"x-goog-api-key": self.api_key},
                )
            except httpx.TimeoutException as exc:
                self.logger.error(
                    "Gemini request timed out model=%s retry_number=%d",
                    self.model_name,
                    retry_number,
                )
                raise GeminiProviderError(
                    "timeout",
                    "The AI provider did not respond in time.",
                ) from exc
            except httpx.RequestError as exc:
                self.logger.error(
                    "Gemini network failure model=%s retry_number=%d error_type=%s",
                    self.model_name,
                    retry_number,
                    type(exc).__name__,
                )
                raise GeminiProviderError(
                    "network_failure",
                    "A network failure prevented contacting the Gemini service.",
                ) from exc

            if response.status_code in self.RETRYABLE_STATUS_CODES:
                if response.status_code == 429:
                    can_retry = rate_limit_retries < 1
                    rate_limit_retries += 1
                else:
                    can_retry = retry_count < len(self.RETRY_DELAYS_SECONDS)
                    retry_count += 1
                if can_retry:
                    delay = self.RETRY_DELAYS_SECONDS[min(retry_count + rate_limit_retries - 1, len(self.RETRY_DELAYS_SECONDS) - 1)]
                    self.logger.warning(
                        "Gemini transient HTTP failure model=%s endpoint=%s status_code=%d "
                        "retry_number=%d retry_delay_seconds=%d",
                        self.model_name,
                        self.endpoint,
                        response.status_code,
                        retry_number + 1,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                category, message = self._classify_status(response.status_code)
                self.logger.error(
                    "Gemini request exhausted retries model=%s endpoint=%s final_status_code=%d",
                    self.model_name,
                    self.endpoint,
                    response.status_code,
                )
                raise GeminiProviderError(category, message, response.status_code)

            if response.status_code >= 400:
                category, message = self._classify_status(response.status_code)
                self.logger.error(
                    "Gemini non-retryable HTTP failure model=%s endpoint=%s final_status_code=%d",
                    self.model_name,
                    self.endpoint,
                    response.status_code,
                )
                raise GeminiProviderError(category, message, response.status_code)

            self.logger.info(
                "Gemini request completed model=%s endpoint=%s final_status_code=%d retry_number=%d",
                self.model_name,
                self.endpoint,
                response.status_code,
                retry_number,
            )
            return self._extract_text(response)

        raise GeminiProviderError(
            "temporary_service_unavailable",
            "The Gemini service is temporarily unavailable. Please try again in a few moments.",
        )

    def _classify_status(self, status_code: int) -> tuple[str, str]:
        if status_code == 400:
            return "invalid_request", "Gemini rejected the request as invalid (HTTP 400)."
        if status_code == 401:
            return "invalid_api_key", "The Gemini API key was rejected (HTTP 401)."
        if status_code == 403:
            return "permission_denied", "The Gemini API denied access to this model (HTTP 403)."
        if status_code == 404:
            return "model_unavailable", "The configured Gemini model or endpoint was not found (HTTP 404)."
        if status_code == 429:
            return "rate_limited", "The Gemini API quota or rate limit has been exceeded (HTTP 429)."
        if status_code in {500, 502, 503, 504}:
            return (
                "temporary_service_unavailable",
                f"The Gemini service is temporarily experiencing high demand or an outage (HTTP {status_code}). Please try again in a few moments.",
            )
        return "provider_http_error", f"The Gemini API returned an unexpected HTTP status ({status_code})."

    def _extract_text(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except (ValueError, TypeError) as exc:
            raise GeminiProviderError(
                "unexpected_api_response",
                "Gemini returned a malformed API response.",
                response.status_code,
            ) from exc

        candidates = data.get("candidates") if isinstance(data, dict) else None
        if not isinstance(candidates, list) or not candidates:
            raise GeminiProviderError(
                "unexpected_api_response",
                "Gemini returned an API response without any candidates.",
                response.status_code,
            )

        candidate = candidates[0]
        if not isinstance(candidate, dict):
            raise GeminiProviderError(
                "unexpected_api_response",
                "Gemini returned an API response with an invalid candidate.",
                response.status_code,
            )

        content = candidate.get("content", {})
        parts = content.get("parts", []) if isinstance(content, dict) else []
        if not isinstance(parts, list):
            raise GeminiProviderError(
                "unexpected_api_response",
                "Gemini returned an API response with invalid content parts.",
                response.status_code,
            )

        text = "".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text", ""), str)
        ).strip()
        if not text:
            raise GeminiProviderError(
                "unexpected_api_response",
                "Gemini returned an empty or malformed response.",
                response.status_code,
            )
        return text

    def close(self) -> None:
        self.client.close()