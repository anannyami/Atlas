import sys
import unittest
import os
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.chat import ChatMessage, ChatRequest
from models.response_validation import ResponseValidationResult
from services.chat_service import ChatService


class StubProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 800) -> str:
        if self.error is not None:
            raise self.error
        return "assistant response"


class CountingProvider(StubProvider):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def generate(self, prompt: str, *, temperature: float = 0.2, max_tokens: int = 800) -> str:
        self.calls += 1
        return f"answer-{self.calls}"


class PassingValidator:
    def validate(self, response: str, *args, **kwargs) -> ResponseValidationResult:
        return ResponseValidationResult(
            passed=True,
            overall_score=0.9,
            word_count=400,
            hallucination_risk=0.0,
            followup_continuity=1.0,
            category_scores={},
        )


class ChatServiceTests(unittest.TestCase):
    def test_identical_normalized_question_uses_success_cache(self) -> None:
        provider = CountingProvider()
        service = ChatService(provider=provider)
        service.response_validator = PassingValidator()
        analysis = {"repository": {"name": "atlas", "full_name": "acme/atlas"}}

        first = service.generate_answer(ChatRequest(question="Explain the repository", analysis=analysis))
        second = service.generate_answer(ChatRequest(question="  EXPLAIN the repository!!!  ", analysis=analysis))

        self.assertEqual(first.answer, "answer-1")
        self.assertEqual(second.answer, "answer-1")
        self.assertEqual(provider.calls, 1)

    def test_follow_up_questions_bypass_stateless_response_cache(self) -> None:
        provider = CountingProvider()
        service = ChatService(provider=provider)
        service.response_validator = PassingValidator()
        analysis = {"repository": {"name": "atlas", "full_name": "acme/atlas"}}

        service.generate_answer(ChatRequest(question="Explain the repository", analysis=analysis))
        service.generate_answer(ChatRequest(
            question="Why?",
            analysis=analysis,
            conversation=[ChatMessage(role="user", content="Explain the repository")],
        ))

        self.assertEqual(provider.calls, 2)

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

        classification = service.intent_classifier.classify(
            request.question,
            recent_user_messages=["What architecture does this use?"],
        )
        state = service.conversation_state_service.update(
            state=None,
            question=request.question,
            classification=classification,
        )
        brief = service.repository_brief_builder.build(request.analysis)
        prompt = service.build_prompt(request, classification, state, brief)

        self.assertIn("Relevant Repository Context", prompt)
        self.assertIn("acme/atlas", prompt)
        self.assertIn("Explain the architecture.", prompt)
        self.assertIn("Recent Conversation Summary", prompt)
        self.assertIn("What architecture does this use?", prompt)
        self.assertIn("Answer the user's actual question first.", prompt)
        self.assertIn(
            "Useful headings for this question: Short Answer, Architecture Overview, "
            "Main Components, Repository Evidence, Engineering Observations.",
            prompt,
        )
        self.assertNotIn("300–800 words", prompt)

    def test_build_prompt_includes_relevant_line_numbered_source_evidence(self) -> None:
        service = ChatService(provider=StubProvider())
        request = ChatRequest(
            question="Trace the request through the order service code.",
            analysis={
                "repository": {"name": "atlas"},
                "source_evidence": [
                    {
                        "path": "backend/routes/orders.py",
                        "file_type": "source",
                        "start_line": 10,
                        "end_line": 14,
                        "text": "def get_orders():\n    return order_service.list_orders()\n",
                        "truncated": False,
                    },
                    {
                        "path": "README.md",
                        "file_type": "documentation",
                        "start_line": 1,
                        "end_line": 2,
                        "text": "Atlas analyzes repositories.",
                        "truncated": False,
                    },
                ],
                "source_evidence_notes": ["Skipped oversized source evidence: backend/generated.py."],
            },
        )
        classification = service.intent_classifier.classify(request.question)
        state = service.conversation_state_service.update(
            state=None,
            question=request.question,
            classification=classification,
        )

        prompt = service.build_prompt(
            request,
            classification,
            state,
            service.repository_brief_builder.build(request.analysis),
        )

        self.assertIn("### backend/routes/orders.py:10-14", prompt)
        self.assertIn("return order_service.list_orders()", prompt)
        self.assertIn("Evidence limits:", prompt)
        self.assertIn("Skipped oversized source evidence", prompt)
        self.assertIn("cite the supplied path and line range", prompt)

    def test_source_evidence_context_remains_bounded(self) -> None:
        service = ChatService(provider=StubProvider())
        analysis = {
            "source_evidence": [
                {
                    "path": f"src/file_{index}.py",
                    "file_type": "source",
                    "start_line": 1,
                    "end_line": 100,
                    "text": "x" * 10_000,
                    "truncated": False,
                }
                for index in range(40)
            ]
        }

        context = service._source_evidence_context(analysis, "trace the request")

        self.assertLessEqual(context.count("\n### "), 4)
        self.assertLessEqual(len(context), 12_000)
        self.assertIn("### src/file_0.py:1-100", context)

    def test_large_history_and_evidence_produce_bounded_provider_prompt(self) -> None:
        service = ChatService(provider=StubProvider())
        request = ChatRequest(
            question="Trace the request flow.",
            analysis={
                "repository": {"name": "atlas"},
                "source_evidence": [
                    {
                        "path": f"src/file_{index}.py",
                        "file_type": "source",
                        "start_line": 1,
                        "end_line": 500,
                        "text": ("def handler():\n    return service.call()\n" * 500),
                        "truncated": False,
                    }
                    for index in range(50)
                ],
            },
            conversation=[
                ChatMessage(role="user", content="previous " + ("history " * 500))
                for _ in range(20)
            ],
        )
        classification = service.intent_classifier.classify(request.question)
        state = service.conversation_state_service.update(
            state=None,
            question=request.question,
            classification=classification,
        )

        prompt = service.build_prompt(
            request,
            classification,
            state,
            service.repository_brief_builder.build(request.analysis),
        )

        self.assertLessEqual(len(prompt), service.MAX_PROVIDER_PROMPT_CHARS)
        self.assertIn("Trace the request flow.", prompt)
        self.assertIn("### src/file_0.py:1-500", prompt)
        self.assertLessEqual(prompt.count("User asked:"), 6)

    def test_architecture_prompt_qualifies_heuristics_and_rejects_unsupported_inferences(self) -> None:
        provider = Mock(spec=["generate"])
        provider.generate.return_value = (
            "The analyzer heuristically labels the repository as Monolith and Layered Application; "
            "the supplied evidence does not confirm either architecture. Flask is detected, but its "
            "use, REST semantics, triggering source file, and deployment configuration cannot be "
            "determined from the framework, CI, directory, and count signals alone."
        )
        service = ChatService(provider=provider)
        service.response_validator = PassingValidator()
        request = ChatRequest(
            question="How is the architecture structured?",
            analysis={
                "repository": {"name": "atlas"},
                "architecture": {
                    "style": "Monolith",
                    "confidence": 0.6,
                    "summary": "The repository most closely matches a monolith architecture.",
                    "applications": ["Web"],
                    "workspace": ["Monorepo"],
                    "api_styles": [{"name": "REST", "confidence": 0.8, "evidence": ["backend stack"]}],
                    "architecture_patterns": [
                        {"name": "Layered Application", "confidence": 0.75, "evidence": ["backend", "services"]}
                    ],
                    "deployment": ["GitHub Actions"],
                    "modules": ["backend", "services"],
                    "backend_frameworks": [
                        {"name": "Flask", "confidence": 0.9, "evidence": ["Flask"]}
                    ],
                },
                "tech_stack": {
                    "backend": ["Flask"],
                    "ci_cd": ["GitHub Actions"],
                },
                "structure": {
                    "total_files": 48,
                    "total_directories": 8,
                    "major_directories": ["backend", "services"],
                },
                "classification": {
                    "project_type": "Web application",
                    "primary_classification": "REST API",
                },
                "blueprint": {
                    "architecture_type": "Layered Application",
                    "confidence": 0.75,
                    "layers": [{"name": "Backend", "directories": ["backend"]}],
                    "data_flow": [{"source": "routes", "target": "services"}],
                },
            },
        )

        response = service.generate_answer(request)
        prompt = provider.generate.call_args.args[0]

        self.assertIn("Heuristic style classification (not source-confirmed): Monolith", prompt)
        self.assertIn("Heuristic application-type signals (not confirmed runtime shape): Web", prompt)
        self.assertIn("Heuristic API-style signals (not API-contract evidence): REST", prompt)
        self.assertIn("Detected CI/container signals (not deployment evidence): GitHub Actions", prompt)
        self.assertIn("Heuristic blueprint architecture type (not confirmed): Layered Application", prompt)
        self.assertIn("Detected backend framework signals (evidence may not identify source files)", prompt)
        self.assertIn(
            "Analyzer classification (heuristic; not proof of architecture): REST API",
            prompt,
        )
        self.assertIn("Detected backend technologies (not API-style or usage evidence): Flask", prompt)
        self.assertIn("does not establish REST semantics", prompt)
        self.assertIn("do not establish deployment configuration", prompt)
        self.assertIn("Directory names, file counts, release counts, and activity metrics do not establish", prompt)
        self.assertIn("Cite framework-triggering source paths only if the analysis supplies them", prompt)
        self.assertIn("The analyzer heuristically labels the repository as Monolith and Layered Application", response.answer)
        self.assertIn("the supplied evidence does not confirm either architecture", response.answer)
        self.assertIn("Flask is detected, but its use, REST semantics, triggering source file, and deployment configuration cannot be determined", response.answer)
        self.assertNotIn("- Style: Monolith", prompt)
        self.assertNotIn("- API styles: REST", prompt)
        self.assertNotIn("- Deployment signals: GitHub Actions", prompt)

    def test_architecture_prompt_retains_explicit_component_evidence(self) -> None:
        provider = Mock(spec=["generate"])
        provider.generate.return_value = (
            "The supplied evidence states that GET /orders dispatches to OrderService. "
            "It does not establish additional responsibilities or deployment behavior."
        )
        service = ChatService(provider=provider)
        service.response_validator = PassingValidator()
        request = ChatRequest(
            question="How is the architecture structured?",
            analysis={
                "repository": {"name": "atlas"},
                "architecture": {"style": "Layered"},
                "knowledge": {
                    "evidence": [
                        {
                            "source": "backend/routes/orders.py",
                            "details": "GET /orders dispatches to OrderService.",
                        }
                    ]
                },
            },
        )

        response = service.generate_answer(request)
        prompt = provider.generate.call_args.args[0]

        self.assertIn("backend/routes/orders.py: GET /orders dispatches to OrderService.", prompt)
        self.assertIn("Describe a component or flow only when supplied evidence explicitly supports it", prompt)
        self.assertIn("GET /orders dispatches to OrderService", response.answer)

    def test_missing_gemini_configuration_returns_clear_error(self) -> None:
        service = ChatService(provider=StubProvider(ValueError("GEMINI_API_KEY is not configured")))
        request = ChatRequest(
            question="Explain the architecture.",
            analysis={"repository": {"name": "atlas"}},
        )

        response = service.generate_answer(request)

        self.assertIn("Configuration Error", response.answer)
        self.assertIn("AI provider is not configured", response.answer)
        self.assertIsNone(response.validation)

    def test_fallback_messages_classify_common_gemini_failures(self) -> None:
        service = ChatService(provider=StubProvider())
        cases = [
            ("The Gemini API quota or rate limit has been exceeded (HTTP 429).", "AI provider quota or rate limit"),
            ("The Gemini service is temporarily experiencing high demand or an outage (HTTP 503).", "AI provider is temporarily unavailable"),
            ("The AI provider did not respond in time.", "did not respond in time"),
            ("The Gemini API key was rejected (HTTP 401).", "rejected its API key"),
            ("The configured Gemini model or endpoint was not found (HTTP 404).", "Check MODEL_NAME or GROQ_MODEL"),
            ("The Groq request was too large (HTTP 413).", "Request Too Large"),
        ]

        for error, expected_message in cases:
            with self.subTest(error=error):
                response = service._fallback_answer("Question", error)
                self.assertIn(expected_message, response)

    def test_generate_answer_returns_original_text_with_validation(self) -> None:
        provider = StubProvider()
        service = ChatService(provider=provider)
        request = ChatRequest(
            question="Explain the architecture.",
            analysis={"repository": {"name": "atlas", "full_name": "acme/atlas"}},
        )

        response = service.generate_answer(request)

        self.assertEqual(response.answer, "assistant response")
        self.assertIsNotNone(response.validation)
        self.assertGreaterEqual(response.validation.overall_score, 0.0)

    def test_prompt_debug_reports_call_count_and_prompt_metrics(self) -> None:
        service = ChatService(provider=StubProvider())
        request = ChatRequest(
            question="Explain the architecture.",
            analysis={"repository": {"name": "atlas", "full_name": "acme/atlas"}},
        )

        with patch.dict(os.environ, {"PROMPT_DEBUG": "true"}):
            with self.assertLogs("services.chat_service", level="INFO") as captured:
                service.generate_answer(request)

        log_text = "\n".join(captured.output)
        self.assertIn("Prompt section", log_text)
        self.assertIn("section=Question Guidance", log_text)
        self.assertIn("estimated_input_tokens=", log_text)
        self.assertIn("estimated_initial_output_tokens=", log_text)
        self.assertIn("estimated_repair_input_tokens=", log_text)
        self.assertIn("estimated_repair_output_tokens=", log_text)
        self.assertIn("estimated_final_output_tokens=", log_text)
        self.assertIn("estimated_total_tokens=", log_text)
        self.assertIn("logical_gemini_calls=2", log_text)
        self.assertIn("retry_triggered=True", log_text)
        self.assertIn("repair_ms=", log_text)
        self.assertIn("validation_ms=", log_text)
        self.assertIn("total_request_ms=", log_text)
        self.assertIn("score_improvement=", log_text)
        self.assertIn("finish_reason=unavailable_provider_returns_text_only", log_text)

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
