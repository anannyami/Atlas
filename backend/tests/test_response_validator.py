import sys
import unittest
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.response_validator import ResponseValidator


ANALYSIS = {
    "repository": {"name": "atlas", "full_name": "acme/atlas", "owner": "acme"},
    "summary": {"overview": "Atlas helps engineers understand repositories."},
    "purpose": {"what": "Repository intelligence assistant", "why": "Explain repository structure and design."},
    "architecture": {"style": "Layered", "summary": "API routes delegate to service modules."},
    "tech_stack": {
        "languages": ["Python", "TypeScript"],
        "backend": ["FastAPI"],
        "frontend": ["React"],
        "technologies": [
            {"name": "FastAPI", "category": "backend", "evidence": ["requirements.txt"]},
            {"name": "React", "category": "frontend", "evidence": ["package.json"]},
        ],
    },
    "structure": {"major_directories": ["backend", "src"], "entry_points": ["backend/main.py"]},
    "knowledge": {"readme": "Atlas Repository Intelligence Assistant"},
    "health": {"score": 78, "overall_status": "Good"},
    "activity": {"activity_level": "Moderate", "repository_maturity": "Growing"},
}


GOOD_RESPONSE = """# Short Answer
Atlas is a repository intelligence application with a layered backend and a React frontend. The supplied analysis shows FastAPI in the backend stack and identifies API routes and service modules in the repository structure.

# Architecture Overview
The repository is identified as acme/atlas and its summary says it helps engineers understand repositories. The purpose analysis describes a repository intelligence assistant. These purpose signals align with the documented Python and TypeScript implementation and the detected frontend and backend technologies.

# Main Components
The architecture summary reports that API routes delegate to service modules, and the architecture style is classified as Layered. That is supported by the structure evidence: backend/main.py is an entry point and the top-level organization includes backend and src. The analysis therefore supports a separation between request-facing backend code and frontend code, although it does not provide enough source detail to infer every runtime interaction.

FastAPI is a detected backend technology with requirements.txt as evidence, while React is detected from package.json. Together with the Python and TypeScript language signals, these findings describe a split web application rather than a single-language codebase. A likely engineering benefit of this organization is clearer responsibility boundaries; the tradeoff is that cross-layer behavior must remain consistent across separate frontend and backend code.

# Repository Evidence
- Repository identity: acme/atlas; the summary says Atlas helps engineers understand repositories.
- Architecture: Layered; the summary states that API routes delegate to service modules.
- Technology: FastAPI is supported by requirements.txt, and React by package.json.
- Structure: backend/main.py is an entry point; backend and src are identified as major directories.
- Health and activity: the supplied analysis reports a health score of 78 (Good) and Moderate activity with Growing maturity.

# Engineering Observations
The layered route-to-service organization and distinct frontend/backend technology signals indicate modular boundaries. That can improve maintainability when responsibilities remain clear, while changes spanning both sides require coordinated updates. The health score and activity labels are repository-level analyzer outputs, not proof of source-code quality or delivery cadence; they should be interpreted alongside the checks and fetched sample limits.

# Conclusion
The available evidence describes Atlas as a layered repository intelligence application using FastAPI and React. Its organization suggests useful modular separation, with the main engineering consideration being coordination across frontend and backend boundaries."""


class ResponseValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ResponseValidator()

    def test_accepts_repository_specific_synthesized_response(self) -> None:
        result = self.validator.validate(GOOD_RESPONSE, ANALYSIS, "Explain the architecture")
        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_sections, [])
        self.assertGreaterEqual(result.overall_score, ResponseValidator.PASS_THRESHOLD)
        self.assertGreaterEqual(len(result.synthesized_areas), 3)

    def test_flags_weak_generic_response(self) -> None:
        response = """# Short Answer
This repository appears to be a software project.
# Repository Overview
In general, repositories contain code.
# Detailed Explanation
It seems to use standard engineering practices.
# Repository Evidence
No specific evidence is available here.
# Engineering Observations
Projects likely benefit from good maintainability.
# Conclusion
This project likely works as expected."""
        result = self.validator.validate(response, ANALYSIS, "Explain this repository")
        self.assertTrue(result.generic_reasoning)
        self.assertFalse(result.passed)
        self.assertTrue(result.missing_repository_evidence)

    def test_reports_missing_headings(self) -> None:
        result = self.validator.validate(
            "# Short Answer\nAtlas is acme/atlas and uses FastAPI.",
            ANALYSIS,
            "Explain the repository",
        )
        self.assertIn("Repository Overview", result.missing_sections)
        self.assertIn("Repository Evidence", result.missing_sections)
        self.assertNotIn("Conclusion", result.missing_sections)
        self.assertFalse(result.passed)

    def test_reports_evidence_section_without_repository_facts(self) -> None:
        response = re.sub(
            r"# Repository Evidence\n.*?(?=\n# Engineering Observations)",
            "# Repository Evidence\n- Common web applications use familiar patterns.\n",
            GOOD_RESPONSE,
            flags=re.DOTALL,
        )
        result = self.validator.validate(response, ANALYSIS, "Explain the repository")
        self.assertTrue(result.missing_repository_evidence)

    def test_response_length_is_not_forced_to_300_words(self) -> None:
        response = """# Short Answer
Atlas helps engineers understand repositories.
# Repository Overview
The supplied summary describes Atlas as a repository intelligence assistant.
# Repository Evidence
Atlas helps engineers understand repositories.
"""
        result = self.validator.validate(response, ANALYSIS, "What is this repository about?")
        self.assertEqual(result.missing_sections, [])
        self.assertEqual(result.category_scores["length"], 1.0)
        self.assertNotIn("Response is longer than needed", " ".join(result.issues))

    def test_extracts_standard_headings_and_preserves_section_content(self) -> None:
        response = """# Short Answer
Direct answer.
## Repository Overview
Purpose and capabilities.
### Detailed Explanation
Implementation details.
## Repository Evidence
Evidence content.
## Engineering Observations
Engineering implications.
## Conclusion
Final takeaway.
"""
        sections = self.validator._extract_sections(response)
        self.assertEqual(sections["Short Answer"], "Direct answer.")
        self.assertEqual(sections["Repository Overview"], "Purpose and capabilities.")
        self.assertEqual(sections["Detailed Explanation"], "Implementation details.")
        self.assertEqual(sections["Repository Evidence"], "Evidence content.")
        self.assertEqual(sections["Engineering Observations"], "Engineering implications.")
        self.assertEqual(sections["Conclusion"], "Final takeaway.")

    def test_extracts_heading_aliases_and_bold_or_italic_titles(self) -> None:
        response = """## **Repository Context**
Context text.
### *Explanation*
Explanation text.
## __Key Repository Evidence__
Evidence text.
## ***Engineering Analysis***
Observations text.
## _Engineering Conclusion_
Conclusion text.
"""
        sections = self.validator._extract_sections(response)
        self.assertEqual(sections["Repository Overview"], "Context text.")
        self.assertEqual(sections["Detailed Explanation"], "Explanation text.")
        self.assertEqual(sections["Repository Evidence"], "Evidence text.")
        self.assertEqual(sections["Engineering Observations"], "Observations text.")
        self.assertEqual(sections["Conclusion"], "Conclusion text.")

    def test_empty_sections_and_missing_expected_sections_are_safe(self) -> None:
        sections = self.validator._extract_sections(
            "# Short Answer\n## Repository Overview\nOverview text.\n## Evidence\n"
        )
        self.assertEqual(sections["Short Answer"], "")
        self.assertEqual(sections["Repository Overview"], "Overview text.")
        self.assertEqual(sections["Repository Evidence"], "")

        result = self.validator.validate(
            "# Short Answer\nDirect answer.",
            ANALYSIS,
            "Which technologies are used?",
        )
        self.assertIn("Detected Technologies", result.missing_sections)
        self.assertIn("Repository Evidence", result.missing_sections)

    def test_architecture_required_sections_use_canonical_alias_keys(self) -> None:
        required_sections = self.validator.required_sections_for_question(
            "Explain the architecture."
        )

        self.assertEqual(
            required_sections,
            (
                "Short Answer",
                "Architecture Overview",
                "Main Components",
                "Repository Evidence",
                "Engineering Observations",
            ),
        )
        self.assertTrue(set(required_sections).issubset(self.validator.SECTION_ALIASES))

    def test_general_question_requires_canonical_repository_evidence_section(self) -> None:
        required_sections = self.validator.required_sections_for_question(
            "How are the different parts represented in the supplied information?"
        )

        self.assertEqual(required_sections, ("Short Answer", "Repository Evidence"))
        self.assertTrue(set(required_sections).issubset(self.validator.SECTION_ALIASES))

    def test_all_question_profiles_return_only_canonical_section_names(self) -> None:
        questions = (
            "What is this repository about?",
            "Explain the architecture.",
            "Which technologies are used?",
            "Explain this function's implementation.",
            "How healthy is the repository?",
            "What improvements would you recommend?",
            "How are the different parts represented in the supplied information?",
        )

        for question in questions:
            with self.subTest(question=question):
                required_sections = self.validator.required_sections_for_question(question)
                self.assertTrue(
                    set(required_sections).issubset(self.validator.SECTION_ALIASES),
                    f"Non-canonical section name in {required_sections!r}",
                )

    def test_key_components_heading_maps_to_main_components(self) -> None:
        sections = self.validator._extract_sections(
            "## Key Components\nThe API and service modules have separate responsibilities."
        )

        self.assertEqual(
            sections["Main Components"],
            "The API and service modules have separate responsibilities.",
        )

    def test_simple_followup_does_not_require_all_repository_headings(self) -> None:
        result = self.validator.validate(
            "The routes delegate to service modules, so request handling and business logic remain separate.",
            ANALYSIS,
            "Why?",
            is_follow_up=True,
        )
        self.assertTrue(result.passed, result.issues)
        self.assertTrue(result.evidence_matches)
        self.assertEqual(result.missing_sections, [])
        self.assertEqual(self.validator.required_sections_for_question("Why?", is_follow_up=True), ())

    def test_followup_requires_analysis_evidence_even_with_continuity(self) -> None:
        result = self.validator.validate(
            "It is adequate.",
            ANALYSIS,
            "Why?",
            is_follow_up=True,
            conversation_state={"current_topic": "adequate"},
        )

        self.assertIn(
            "No specific fact from the supplied analysis was identifiable in the response.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_followup_repository_claim_fails_when_analysis_has_no_evidence(self) -> None:
        result = self.validator.validate(
            "The repository is a microservice architecture.",
            {},
            "Why?",
            is_follow_up=True,
        )

        self.assertIn(
            "No extractable repository evidence is available to validate this follow-up response.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_followup_architecture_claim_requires_architecture_evidence(self) -> None:
        result = self.validator.validate(
            "Atlas is a microservice architecture.",
            {"repository": {"name": "atlas"}},
            "Why?",
            is_follow_up=True,
        )

        self.assertIn(
            "The follow-up contains an architectural claim without matching architecture evidence.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_followup_technology_claim_requires_technology_evidence(self) -> None:
        result = self.validator.validate(
            "Atlas uses Django.",
            {"repository": {"name": "atlas"}},
            "Why?",
            is_follow_up=True,
        )

        self.assertIn(
            "The follow-up contains a technology claim without matching technology evidence.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_followup_claim_with_sparse_matching_architecture_evidence_can_pass(self) -> None:
        result = self.validator.validate(
            "The architecture is Layered.",
            {"architecture": {"style": "Layered"}},
            "Why?",
            is_follow_up=True,
        )

        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_followup_supported_technology_does_not_mask_unsupported_technology(self) -> None:
        result = self.validator.validate(
            "Atlas uses FastAPI and Celery.",
            {"tech_stack": {"backend": ["FastAPI"]}},
            "Why?",
            is_follow_up=True,
        )

        self.assertIn(
            "The follow-up contains a technology claim without matching technology evidence.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_followup_supported_architecture_does_not_mask_unsupported_mechanism(self) -> None:
        result = self.validator.validate(
            "Atlas has a Layered architecture that uses message queues.",
            {"architecture": {"style": "Layered"}},
            "Why?",
            is_follow_up=True,
        )

        self.assertIn(
            "The follow-up contains an architectural claim without matching architecture evidence.",
            result.missing_repository_evidence,
        )
        self.assertFalse(result.passed)

    def test_fully_supported_technology_followup_can_pass(self) -> None:
        result = self.validator.validate(
            "Atlas uses FastAPI.",
            {"tech_stack": {"backend": ["FastAPI"]}},
            "Why?",
            is_follow_up=True,
        )

        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_multiple_supported_technology_claims_can_pass(self) -> None:
        result = self.validator.validate(
            "Atlas uses FastAPI and Celery.",
            {"tech_stack": {"backend": ["FastAPI", "Celery"]}},
            "Why?",
            is_follow_up=True,
        )

        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_fully_supported_architecture_followup_can_pass(self) -> None:
        result = self.validator.validate(
            "Atlas has a Layered architecture.",
            {"architecture": {"style": "Layered"}},
            "Why?",
            is_follow_up=True,
        )

        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_supported_architecture_and_mechanism_claims_can_pass(self) -> None:
        result = self.validator.validate(
            "Atlas has a Layered architecture that uses message queues.",
            {
                "architecture": {
                    "style": "Layered",
                    "summary": "The system uses message queues.",
                },
            },
            "Why?",
            is_follow_up=True,
        )

        self.assertTrue(result.passed, result.issues)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_followup_with_matching_repository_evidence_can_pass(self) -> None:
        result = self.validator.validate(
            "The backend architecture is Layered: API routes delegate to service modules. "
            "This keeps request handling separate from service responsibilities.",
            ANALYSIS,
            "Why?",
            is_follow_up=True,
            conversation_state={"current_topic": "architecture", "current_component": "backend"},
        )

        self.assertTrue(result.passed, result.issues)
        self.assertTrue(result.evidence_matches)
        self.assertEqual(result.missing_repository_evidence, [])

    def test_followup_does_not_treat_question_technology_as_repository_evidence(self) -> None:
        result = self.validator.validate(
            "It uses Django.",
            ANALYSIS,
            "Does it use Django?",
            is_follow_up=True,
            conversation_state={"current_topic": "Django"},
        )

        self.assertGreater(result.hallucination_risk, 0.0)
        self.assertTrue(any("Django" in issue for issue in result.issues))
        self.assertFalse(result.passed)

    def test_profile_and_classification_words_do_not_match_code_substrings(self) -> None:
        for question in (
            "What is the profile of this repository?",
            "What is the project classification?",
        ):
            with self.subTest(question=question):
                self.assertEqual(self.validator._response_profile(question, False), "overview")

    def test_ordinary_markdown_and_fenced_code_are_not_section_headings(self) -> None:
        text = """A paragraph containing # Short Answer is ordinary text.

**Bold paragraph**, not a heading.
- ## list text

```markdown
# Repository Evidence
```
"""
        self.assertEqual(self.validator._extract_sections(text), {})

    def test_followup_checks_topic_continuity_and_repetition(self) -> None:
        response = """# Short Answer
Continuing the Backend architecture discussion, the supplied analysis identifies FastAPI and API routes delegating to service modules.
# Repository Overview
For this follow-up, the relevant context is the Layered backend in acme/atlas.
# Detailed Explanation
The architecture summary and backend/main.py entry point support the earlier separation between API handling and service responsibilities. The analysis does not identify authentication implementation details, so its behavior cannot be established from this evidence. This distinction matters for evaluating later scalability or security decisions.
# Repository Evidence
- The architecture summary says API routes delegate to service modules.
- backend/main.py is an entry point and FastAPI is detected from requirements.txt.
# Engineering Observations
Maintaining the route-to-service boundary can support modularity, but authentication behavior is not evidenced in the supplied analysis.
# Conclusion
This extends the Backend architecture discussion while avoiding an unsupported claim about authentication internals."""
        result = self.validator.validate(
            response,
            ANALYSIS,
            "How does authentication work?",
            is_follow_up=True,
            conversation_state={"current_topic": "Architecture", "current_component": "Backend"},
            prior_assistant_responses=["The Backend uses a layered architecture with API routes and service modules."],
        )
        self.assertGreaterEqual(result.followup_continuity, 0.5)

    def test_flags_unsupported_technology_claim(self) -> None:
        response = GOOD_RESPONSE.replace(
            "The architecture summary reports that API routes delegate to service modules",
            "The repository uses Django and its architecture summary reports that API routes delegate to service modules",
        )
        result = self.validator.validate(response, ANALYSIS, "Explain the backend")
        self.assertGreater(result.hallucination_risk, 0.0)
        self.assertTrue(any("unsupported technology" in issue for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
