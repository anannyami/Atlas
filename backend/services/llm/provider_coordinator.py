from __future__ import annotations

import logging
from typing import Any

from services.llm.base_provider import LLMGenerationResult


class ProviderFallbackCoordinator:
    """Use Gemini first and invoke Groq only for transient availability failures or quota."""

    FALLBACK_CATEGORIES = frozenset({
        "rate_limited", "temporary_service_unavailable", "timeout", "network_failure",
    })

    def __init__(self, primary: Any, fallback: Any | None = None) -> None:
        self.primary = primary
        self.fallback = fallback
        self.logger = logging.getLogger(__name__)

    def generate_with_metadata(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1500) -> LLMGenerationResult:
        try:
            return self._generate(self.primary, prompt, temperature, max_tokens)
        except Exception as exc:
            if self.fallback is None or not self._should_fallback(exc):
                raise
            self.logger.warning("Primary LLM unavailable; trying configured fallback category=%s status_code=%s", getattr(exc, "category", "provider_error"), getattr(exc, "status_code", None))
            return self._generate(self.fallback, prompt, temperature, max_tokens)

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1500) -> str:
        result = self.generate_with_metadata(prompt, temperature=temperature, max_tokens=max_tokens)
        if not result.completed:
            raise RuntimeError(f"LLM generation did not complete (finish reason: {result.finish_reason}).")
        return result.text

    @classmethod
    def _should_fallback(cls, exc: Exception) -> bool:
        category = getattr(exc, "category", None)
        status_code = getattr(exc, "status_code", None)
        if status_code == 429:
            return True
        if status_code in {400, 401, 404}:
            return False
        return category in cls.FALLBACK_CATEGORIES

    @staticmethod
    def _generate(provider: Any, prompt: str, temperature: float, max_tokens: int) -> LLMGenerationResult:
        method = getattr(provider, "generate_with_metadata", None)
        if callable(method):
            result = method(prompt, temperature=temperature, max_tokens=max_tokens)
            if not isinstance(result, LLMGenerationResult):
                raise TypeError("Provider returned invalid generation metadata.")
            return result
        text = provider.generate(prompt, temperature=temperature, max_tokens=max_tokens)
        if not isinstance(text, str):
            raise TypeError("Provider returned a non-text response.")
        return LLMGenerationResult(text, "unavailable_provider_returns_text_only", True)

    def close(self) -> None:
        for provider in (self.primary, self.fallback):
            close = getattr(provider, "close", None)
            if callable(close):
                close()
