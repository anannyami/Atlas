import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.chat import ChatMessage, ChatRequest
from services.chat_service import ChatService


class StubProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 800) -> str:
        if self.error is not None:
            raise self.error
        return "assistant response"


class ChatServiceTests(unittest.TestCase):
    def test_build_prompt_includes_repository_context_and_question(self) -> None:
        service = ChatService(provider=StubProvider())
        request = ChatRequest(
            question="Explain the architecture.",
            analysis={
                "repository": {
                    "name": "atlas",
                    "full_name": "acme/atlas",
                    "owner": "acme",
                    "description": "Repository analysis platform",
                    "topics": ["ai", "developer-tools"],
                },
                "summary": {
                    "overview": "A repository analysis platform",
                    "purpose": "Help engineers understand codebases",
                    "highlights": ["fast analysis", "rich insights"],
                    "current_status": "healthy",
                },
                "tech_stack": {
                    "languages": ["TypeScript"],
                    "frontend": ["React"],
                    "backend": ["FastAPI"],
                    "database": ["PostgreSQL"],
                    "cloud": ["Azure"],
                    "ci_cd": ["GitHub Actions"],
                    "package_managers": ["npm"],
                    "containers": ["Docker"],
                    "mobile": [],
                },
                "architecture": {
                    "style": "modular monolith",
                    "confidence": 0.8,
                    "architecture_patterns": [{"name": "layered", "confidence": 0.9, "evidence": []}],
                    "deployment": ["containerized"],
                    "modules": ["backend", "frontend"],
                    "organization": ["services", "components"],
                    "summary": "A layered application",
                },
                "structure": {
                    "summary": "Backend and frontend are separated",
                    "major_folders": ["backend", "src"],
                    "entry_points": ["main.py", "src/main.tsx"],
                    "configuration_files": ["package.json", "requirements.txt"],
                },
                "health": {"score": 79, "overall_status": "good", "checks": {}, "missing_recommendations": []},
                "activity": {"stars": 100, "forks": 20, "open_issues": 5, "recent_commits": 10, "recent_pull_requests": 3, "releases": 2, "community_size": "medium", "activity_level": "active", "maintenance_status": "healthy", "repository_maturity": "maturing"},
                "classification": {"project_type": "Application", "primary_classification": "Developer tool"},
            },
            conversation=[
                ChatMessage(role="user", content="What architecture does this use?"),
                ChatMessage(role="assistant", content="A modular architecture."),
            ],
        )

        prompt = service.build_prompt(request)

        self.assertIn("Repository Information", prompt)
        self.assertIn("acme/atlas", prompt)
        self.assertIn("Explain the architecture.", prompt)
        self.assertIn("Conversation History", prompt)
        self.assertIn("What architecture does this use?", prompt)

    def test_missing_gemini_configuration_returns_clear_error(self) -> None:
        service = ChatService(provider=StubProvider(ValueError("GEMINI_API_KEY is not configured")))
        request = ChatRequest(
            question="Explain the architecture.",
            analysis={"repository": {"name": "atlas"}},
        )

        response = service.generate_answer(request)

        self.assertIn("Configuration Error", response.answer)
        self.assertIn("GEMINI_API_KEY", response.answer)

    def test_build_context_includes_repository_tree_for_folder_questions(self) -> None:
        service = ChatService(provider=StubProvider())
        request = ChatRequest(
            question="Explain the folder structure.",
            analysis={
                "repository": {"name": "atlas"},
                "structure": {"summary": "Backend and frontend are separated", "entry_points": ["backend/app.py"]},
                "repository_tree": [
                    {"name": "backend", "path": "backend", "type": "directory", "children": [{"name": "app.py", "path": "backend/app.py", "type": "file", "children": []}]}
                ],
            },
        )

        context = service.build_context(request.analysis)

        self.assertIn("Repository Tree", context)
        self.assertIn("backend/app.py", context)


if __name__ == "__main__":
    unittest.main()
