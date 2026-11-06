from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMGenerationResult:
    text: str
    finish_reason: str
    completed: bool
    prompt_token_count: int | None = None
    candidates_token_count: int | None = None
    thoughts_token_count: int | None = None
    total_token_count: int | None = None


class LLMProvider(Protocol):
    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 800) -> str:
        ...
