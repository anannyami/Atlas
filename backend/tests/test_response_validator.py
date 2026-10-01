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

# Repository Overview
The repository is identified as acme/atlas and its summary says it helps engineers understand repositories. The purpose analysis describes a repository intelligence assistant. These purpose signals align with the documented Python and TypeScript implementation and the detected frontend and backend technologies.

# Detailed Explanation
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
        self.assertIn("Conclusion", result.missing_sections)
        self.assertIn("Detailed Explanation", result.missing_sections)
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

    def test_scores_very_short_response_low_for_normal_question(self) -> None:
        response = """# Short Answer
Atlas uses FastAPI.
# Repository Overview
acme/atlas is a repository tool.
# Detailed Explanation
FastAPI provides its API.
# Repository Evidence
FastAPI appears in requirements.txt.
# Engineering Observations
The backend is modular.
# Conclusion
Atlas is layered."""
        result = self.validator.validate(response, ANALYSIS, "Explain the architecture")
        self.assertLess(result.category_scores["length"], 1.0)
        self.assertIn("300–800 word range", " ".join(result.issues))

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
