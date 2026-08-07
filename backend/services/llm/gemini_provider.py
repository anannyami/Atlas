from __future__ import annotations
from core.config import settings
import os
from typing import Any

import httpx

from services.llm.base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.MODEL_NAME
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        print("GEMINI =", settings.GEMINI_API_KEY)

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        url = (
            f"{self.base_url}/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        print("=" * 80)
        print("MODEL :", self.model_name)
        print("URL   :", url.replace(self.api_key, "***API_KEY_HIDDEN***"))
        print("TEMP  :", temperature)
        print("TOKENS:", max_tokens)
        print("=" * 80)

        try:
            with httpx.Client(timeout=120.0) as client:
                print("=" * 80)
                print("MODEL :", self.model_name)
                print("URL   :", url.replace(self.api_key, "***API_KEY_HIDDEN***"))
                print("TEMP  :", temperature)
                print("TOKENS:", max_tokens)
                print("API KEY PREFIX:", self.api_key[:15])
                print("=" * 80)
                response = client.post(url, json=payload)

            if response.status_code != 200:
                print("=" * 80)
                print("STATUS :", response.status_code)
                print("BODY:")
                print(response.text)
                print("=" * 80)
                response.raise_for_status()

            data = response.json()

        except httpx.HTTPStatusError:
            raise

        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Failed to connect to Gemini API: {exc}"
            ) from exc

        candidates = data.get("candidates", [])

        if not candidates:
            raise ValueError(f"No candidates returned.\nResponse:\n{data}")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        text = "".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict)
        ).strip()

        if not text:
            raise ValueError(f"Gemini returned an empty response.\nResponse:\n{data}")

        return text