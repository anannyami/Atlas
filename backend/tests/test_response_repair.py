import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.chat import ChatRequest
from models.response_validation import ResponseValidationResult
from services.chat_service import ChatService
from services.llm.base_provider import LLMGenerationResult


class QueuedProvider:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 1500) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


class QueuedMetadataProvider(QueuedProvider):
    def __init__(self, results: list[LLMGenerationResult | Exception]) -> None:
        self.results = list(results)
        self.prompts: list[str] = []

    def generate_with_metadata(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1500,
    ) -> LLMGenerationResult:
        self.prompts.append(prompt)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class QueuedValidator:
    def __init__(self, results: list[ResponseValidationResult]) -> None:
        self.results = list(results)
        self.responses: list[str] = []

    def validate(self, response: str, *args, **kwargs) -> ResponseValidationResult:
        self.responses.append(response)
        return self.results.pop(0)


def result(
    passed: bool,
    score: float,
    *,
    issues: list[str] | None = None,
    missing_sections: list[str] | None = None,
    missing_repository_evidence: list[str] | None = None,
) -> ResponseValidationResult:
    return ResponseValidationResult(
        passed=passed,
        overall_score=score,
        word_count=120,
        missing_sections=missing_sections or [],
        missing_repository_evidence=missing_repository_evidence or [],
        missing_engineering_observations=[],
        generic_reasoning=False,
        hallucination_risk=0.0,
        followup_continuity=1.0,
        issues=issues or [],
        category_scores={},
        evidence_matches=[],
        synthesized_areas=[],
    )


def service_with(provider: QueuedProvider, validations: list[ResponseValidationResult]) -> tuple[ChatService, QueuedValidator]:
    service = ChatService(provider=provider)
    validator = QueuedValidator(validations)
    service.response_validator = validator
    return service, validator


def request() -> ChatRequest:
    return ChatRequest(
        question="Explain the Atlas architecture.",
        analysis={
            "repository": {"name": "atlas", "full_name": "acme/atlas"},
            "architecture": {"style": "Layered", "summary": "Routes delegate to services."},
            "tech_stack": {"backend": ["FastAPI"]},
        },
    )


class ResponseRepairTests(unittest.TestCase):
    def test_repair_is_not_triggered_for_passing_response(self) -> None:
        provider = QueuedProvider(["original valid answer"])
        service, validator = service_with(provider, [result(True, 0.91)])

        response = service.generate_answer(request())

        self.assertEqual(response.answer, "original valid answer")
        self.assertTrue(response.validation.passed)
        self.assertEqual(len(provider.prompts), 1)
        self.assertEqual(len(validator.responses), 1)

    def test_minor_low_score_without_major_failure_does_not_repair(self) -> None:
        provider = QueuedProvider(["short but supported answer", "must not be requested"])
        service, validator = service_with(provider, [
            result(True, 0.61, issues=["Response length is outside the expected 300–800 word range."]),
        ])
        response = service.generate_answer(request())
        self.assertEqual(response.answer, "short but supported answer")
        self.assertEqual(len(provider.prompts), 1)
        self.assertEqual(len(validator.responses), 1)

    def test_failed_validation_triggers_repair_with_specific_reasons(self) -> None:
        provider = QueuedProvider(["weak original", "repaired answer"])
        service, validator = service_with(provider, [
            result(
                False,
                0.42,
                issues=["Response is missing one or more required contract sections."],
                missing_sections=["Repository Evidence", "Conclusion"],
                missing_repository_evidence=["No supplied repository fact was identified."],
            ),
            result(True, 0.83),
        ])

        response = service.generate_answer(request())

        self.assertEqual(response.answer, "repaired answer")
        self.assertTrue(response.validation.passed)
        self.assertEqual(len(provider.prompts), 2)
        repair_prompt = provider.prompts[1]
        self.assertIn("weak original", repair_prompt)
        self.assertIn("Repository Evidence", repair_prompt)
        self.assertIn("No supplied repository fact was identified", repair_prompt)
        self.assertIn("Explain the Atlas architecture.", repair_prompt)
        self.assertIn("acme/atlas", repair_prompt)
        self.assertEqual(len(validator.responses), 2)

    def test_repair_improvement_uses_second_validation_score(self) -> None:
        provider = QueuedProvider(["weak answer", "improved answer"])
        service, _ = service_with(provider, [result(False, 0.31, missing_sections=["Repository Evidence"]), result(True, 0.88)])

        response = service.generate_answer(request())

        self.assertEqual(response.answer, "improved answer")
        self.assertGreater(response.validation.overall_score, 0.31)

    def test_repair_response_is_returned_even_if_second_validation_fails(self) -> None:
        provider = QueuedProvider(["weak answer", "better but still incomplete"])
        service, _ = service_with(provider, [
            result(False, 0.35, missing_sections=["Repository Evidence"]),
            result(False, 0.58, missing_sections=["Conclusion"]),
        ])

        response = service.generate_answer(request())

        self.assertEqual(response.answer, "better but still incomplete")
        self.assertFalse(response.validation.passed)
        self.assertEqual(response.validation.overall_score, 0.58)
        self.assertEqual(len(provider.prompts), 2)

    def test_retry_limit_is_one_even_when_second_validation_fails(self) -> None:
        provider = QueuedProvider(["first", "second", "must not be requested"])
        service, validator = service_with(provider, [
            result(False, 0.2, issues=["first failure"], missing_sections=["Repository Evidence"]),
            result(False, 0.4, issues=["second failure"]),
        ])

        response = service.generate_answer(request())

        self.assertEqual(response.answer, "second")
        self.assertEqual(len(provider.prompts), 2)
        self.assertEqual(len(validator.responses), 2)
        self.assertEqual(provider.responses, ["must not be requested"])

    def test_initial_provider_failure_does_not_trigger_repair(self) -> None:
        provider = QueuedMetadataProvider([RuntimeError("provider unavailable")])
        service, validator = service_with(provider, [
            result(False, 0.2, missing_sections=["Repository Evidence"]),
        ])

        response = service.generate_answer(request())

        self.assertIn("provider is unavailable", response.answer)
        self.assertEqual(len(provider.prompts), 1)
        self.assertEqual(len(validator.responses), 0)
        self.assertIsNone(response.validation)

    def test_incomplete_initial_generation_is_not_presented_or_repaired(self) -> None:
        provider = QueuedMetadataProvider([
            LLMGenerationResult("partial secret answer", "MAX_TOKENS", False),
        ])
        service, validator = service_with(provider, [
            result(False, 0.2, missing_sections=["Repository Evidence"]),
        ])

        response = service.generate_answer(request())

        self.assertIn("Incomplete AI Response", response.answer)
        self.assertIn("MAX_TOKENS", response.answer)
        self.assertNotIn("partial secret answer", response.answer)
        self.assertEqual(len(provider.prompts), 1)
        self.assertEqual(len(validator.responses), 0)
        self.assertIsNone(response.validation)

    def test_incomplete_repair_keeps_original_and_surfaces_diagnostic(self) -> None:
        provider = QueuedMetadataProvider([
            LLMGenerationResult("weak original answer", "STOP", True),
            LLMGenerationResult("partial repaired answer", "MAX_TOKENS", False),
        ])
        service, validator = service_with(provider, [
            result(False, 0.3, missing_sections=["Repository Evidence"]),
        ])

        with self.assertLogs("services.chat_service", level="WARNING") as captured:
            response = service.generate_answer(request())

        self.assertEqual(response.answer, "weak original answer")
        self.assertIn("Repository Evidence", response.validation.missing_sections)
        self.assertIn("Repair response was incomplete (MAX_TOKENS).", "\n".join(captured.output))
        self.assertEqual(len(provider.prompts), 2)
        self.assertEqual(len(validator.responses), 1)
        self.assertNotIn("required six-section", provider.prompts[1])


if __name__ == "__main__":
    unittest.main()
