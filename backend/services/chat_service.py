from __future__ import annotations
from core.config import settings
import os
import re
from typing import Any

from models.chat import ChatRequest, ChatResponse, ChatSource
from services.llm.gemini_provider import GeminiProvider


class ChatService:
    """Generate repository-aware answers from Atlas analysis output."""

    def __init__(self, provider: Any | None = None) -> None:
        self.provider = provider or self._build_provider()

    def _build_provider(self) -> Any:
        provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
        if provider_name != "gemini":
            return GeminiProvider()
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model_name=settings.MODEL_NAME,
        )

    def _join(self, values: list[Any] | tuple[Any, ...] | None) -> str:
        if not values:
            return "Unavailable"
        return ", ".join(str(value) for value in values if value)

    def _normalise_text(self, value: Any) -> str:
        if value is None:
            return "Unavailable"
        if isinstance(value, (list, tuple, set)):
            return self._join(list(value))
        if isinstance(value, dict):
            return ", ".join(f"{key}: {item}" for key, item in value.items())
        return str(value)

    def _build_section(self, title: str, lines: list[str]) -> str:
        return "\n".join([f"## {title}", *lines, ""])

    def build_context(self, analysis: dict[str, Any]) -> str:
        repository = analysis.get("repository") or {}
        summary = analysis.get("summary") or {}
        architecture = analysis.get("architecture") or {}
        structure = analysis.get("structure") or {}
        tech_stack = analysis.get("tech_stack") or {}
        health = analysis.get("health") or {}
        activity = analysis.get("activity") or {}
        classification = analysis.get("classification") or {}
        purpose = analysis.get("purpose") or {}
        readme_summary = analysis.get("readme_summary") or analysis.get("readme") or {}
        product_identity = analysis.get("product_identity") or {}
        repository_identity = analysis.get("repository_identity") or {}
        knowledge = analysis.get("knowledge") or {}
        blueprint = analysis.get("blueprint") or {}
        repository_dna = analysis.get("repository_dna") or analysis.get("dna") or {}
        repository_tree = analysis.get("repository_tree") or []

        architecture_patterns = architecture.get("architecture_patterns") or []
        pattern_names = []
        for pattern in architecture_patterns:
            if isinstance(pattern, dict):
                name = pattern.get("name")
                if name:
                    pattern_names.append(name)

        sections: list[str] = []
        sections.append(self._build_section("Repository Metadata", [
            f"- Name: {repository.get('name') or 'Unavailable'}",
            f"- Full Name: {repository.get('full_name') or 'Unavailable'}",
            f"- Owner: {repository.get('owner') or 'Unavailable'}",
            f"- Description: {repository.get('description') or 'Unavailable'}",
            f"- Topics: {self._join(repository.get('topics') or [])}",
            f"- Stars: {self._normalise_text(activity.get('stars'))}",
            f"- Forks: {self._normalise_text(activity.get('forks'))}",
            f"- Open Issues: {self._normalise_text(activity.get('open_issues'))}",
        ]))

        sections.append(self._build_section("Repository Summary", [
            f"- Overview: {self._normalise_text(summary.get('overview'))}",
            f"- Purpose: {self._normalise_text(summary.get('purpose'))}",
            f"- Current Status: {self._normalise_text(summary.get('current_status'))}",
            f"- Highlights: {self._join(summary.get('highlights') or [])}",
            f"- Source Factors: {self._join(summary.get('source_factors') or [])}",
        ]))

        sections.append(self._build_section("Project Classification", [
            f"- Project Type: {self._normalise_text(classification.get('project_type'))}",
            f"- Primary Classification: {self._normalise_text(classification.get('primary_classification'))}",
            f"- Confidence: {self._normalise_text(classification.get('confidence'))}",
        ]))

        sections.append(self._build_section("Purpose", [
            f"- What: {self._normalise_text(purpose.get('what'))}",
            f"- Why: {self._normalise_text(purpose.get('why'))}",
            f"- Audience: {self._normalise_text(purpose.get('audience'))}",
            f"- Problem: {self._normalise_text(purpose.get('problem'))}",
            f"- Capabilities: {self._join(purpose.get('capabilities') or [])}",
            f"- Technology Story: {self._normalise_text(purpose.get('technology_story'))}",
        ]))

        sections.append(self._build_section("Architecture", [
            f"- Style: {self._normalise_text(architecture.get('style'))}",
            f"- Confidence: {self._normalise_text(architecture.get('confidence'))}",
            f"- Patterns: {self._join(pattern_names)}",
            f"- Deployment: {self._join(architecture.get('deployment') or [])}",
            f"- Modules: {self._join(architecture.get('modules') or [])}",
            f"- Organization: {self._join(architecture.get('organization') or [])}",
            f"- Summary: {self._normalise_text(architecture.get('summary'))}",
            f"- Frontend Frameworks: {self._join([item.get('name') for item in (architecture.get('frontend_frameworks') or []) if isinstance(item, dict)])}",
            f"- Backend Frameworks: {self._join([item.get('name') for item in (architecture.get('backend_frameworks') or []) if isinstance(item, dict)])}",
            f"- Databases: {self._join([item.get('name') for item in (architecture.get('databases') or []) if isinstance(item, dict)])}",
            f"- Cloud: {self._join([item.get('name') for item in (architecture.get('cloud') or []) if isinstance(item, dict)])}",
            f"- Authentication: {self._join([item.get('name') for item in (architecture.get('authentication') or []) if isinstance(item, dict)])}",
        ]))

        sections.append(self._build_section("Repository Identity", [
            f"- Product Name: {self._normalise_text(repository_identity.get('product_name'))}",
            f"- Category: {self._normalise_text(repository_identity.get('category'))}",
            f"- Subtype: {self._normalise_text(repository_identity.get('subtype'))}",
            f"- Tagline: {self._normalise_text(repository_identity.get('tagline'))}",
            f"- Description: {self._normalise_text(repository_identity.get('description'))}",
            f"- Audience: {self._normalise_text(repository_identity.get('audience'))}",
            f"- Capabilities: {self._join(repository_identity.get('capabilities') or [])}",
            f"- Evidence: {self._join(repository_identity.get('evidence') or [])}",
        ]))

        sections.append(self._build_section("Repository DNA", [
            f"- Engineering Style: {self._normalise_text(repository_dna.get('engineering_style'))}",
            f"- Maturity: {self._normalise_text(repository_dna.get('maturity'))}",
            f"- Strengths: {self._join(repository_dna.get('strengths') or [])}",
            f"- Traits: {self._join([trait.get('name') for trait in (repository_dna.get('traits') or []) if isinstance(trait, dict)])}",
            f"- Confidence: {self._normalise_text(repository_dna.get('confidence'))}",
        ]))

        sections.append(self._build_section("Tech Stack", [
            f"- Languages: {self._join(tech_stack.get('languages') or [])}",
            f"- Frontend: {self._join(tech_stack.get('frontend') or [])}",
            f"- Backend: {self._join(tech_stack.get('backend') or [])}",
            f"- Database: {self._join(tech_stack.get('database') or [])}",
            f"- Cloud: {self._join(tech_stack.get('cloud') or [])}",
            f"- CI/CD: {self._join(tech_stack.get('ci_cd') or [])}",
            f"- Package Managers: {self._join(tech_stack.get('package_managers') or [])}",
            f"- Containers: {self._join(tech_stack.get('containers') or [])}",
            f"- Mobile: {self._join(tech_stack.get('mobile') or [])}",
            f"- Detected Technologies: {self._join([item.get('name') for item in (tech_stack.get('technologies') or []) if isinstance(item, dict)])}",
        ]))

        sections.append(self._build_section("Repository Structure", [
            f"- Summary: {self._normalise_text(structure.get('summary'))}",
            f"- Major Directories: {self._join(structure.get('major_directories') or [])}",
            f"- Largest Directories: {self._join([item.get('path') for item in (structure.get('largest_directories') or []) if isinstance(item, dict)])}",
            f"- Major Modules: {self._join(structure.get('major_modules') or [])}",
            f"- Entry Points: {self._join(structure.get('entry_points') or [])}",
            f"- Important Folders: {self._join(structure.get('important_folders') or [])}",
            f"- Configuration Files: {self._join(structure.get('configuration_files') or [])}",
        ]))

        if repository_tree:
            tree_lines = []
            def _render_tree(nodes: list[dict[str, Any]], indent: int = 0) -> None:
                for node in nodes:
                    tree_lines.append("  " * indent + f"- {node.get('name')} ({node.get('path')})")
                    children = node.get("children") or []
                    if children:
                        _render_tree(children, indent + 1)
            _render_tree(repository_tree)
            sections.append(self._build_section("Repository Tree", tree_lines))

        sections.append(self._build_section("README Summary", [
            self._normalise_text(readme_summary.get('summary') or readme_summary.get('overview') or readme_summary.get('content') or readme_summary),
        ]))

        sections.append(self._build_section("Health and Activity", [
            f"- Score: {self._normalise_text(health.get('score'))}",
            f"- Overall Status: {self._normalise_text(health.get('overall_status'))}",
            f"- Checks: {self._normalise_text(health.get('checks'))}",
            f"- Recommendations: {self._join(health.get('missing_recommendations') or [])}",
            f"- Activity Level: {self._normalise_text(activity.get('activity_level'))}",
            f"- Maintenance Status: {self._normalise_text(activity.get('maintenance_status'))}",
            f"- Repository Maturity: {self._normalise_text(activity.get('repository_maturity'))}",
            f"- Recent Commits: {self._normalise_text(activity.get('recent_commits'))}",
            f"- Recent PRs: {self._normalise_text(activity.get('recent_pull_requests'))}",
            f"- Releases: {self._normalise_text(activity.get('releases'))}",
        ]))

        sections.append(self._build_section("Knowledge and Blueprint", [
            f"- Knowledge Summary: {self._normalise_text(knowledge.get('summary'))}",
            f"- Blueprint Summary: {self._normalise_text(blueprint.get('summary'))}",
        ]))

        return "\n".join(sections)

    def build_prompt(self, request: ChatRequest) -> str:
        context = self.build_context(request.analysis)
        conversation = request.conversation or []
        history_lines = []
        if conversation:
            for message in conversation[-6:]:
                history_lines.append(f"- {message.role.title()}: {message.content}")

        history_block = "\n".join(history_lines) if history_lines else "- No prior conversation"
        question = request.question.strip()
        selected_context = self.select_context(question)
        selected_context_text = ", ".join(selected_context) if selected_context else "Full repository analysis"

        if selected_context:
            context = self._extract_context(context, selected_context)

        return f"""{self.build_system_prompt()}

{self.build_question_guidance(question)}

{self.build_response_template()}

Selected Context
================
{selected_context_text}

Repository Information
=====================
{context}

Conversation History
====================
{history_block}

User Question:
{question}
"""

    def build_system_prompt(self) -> str:
        return (
            "You are Atlas, an AI repository engineer and senior software architect. "
            "The repository analysis object supplied below is the sole source of truth. "
            "Do not invent features, frameworks, technologies, cloud providers, build systems, authentication, or architecture patterns. "
            "If the repository analysis does not contain enough evidence for the question, respond exactly with: 'Based on the available repository analysis I cannot determine that.' "
            "Answer with confidence only when evidence is present, and explain your reasoning using repository evidence. "
            "Use markdown headings, lists, tables, and concrete citations. "
            "Do not answer generically or with vague speculation. "
            "Always keep the response anchored to the repository analysis, and treat the analysis as the authoritative source."
        )

    def build_response_template(self) -> str:
        """
        Response contract for Atlas.

        Gemini should treat this as a required output structure,
        not as an optional formatting suggestion.
        """

        return """
    You MUST follow the structure below.

    IMPORTANT RULES

    - Complete EVERY section.
    - Do NOT omit headings.
    - Do NOT stop after the Short Answer.
    - Unless the user explicitly asks for a short answer, produce approximately 300–800 words.
    - Every important statement should be supported by repository evidence.
    - Never invent repository features or technologies.
    - Tailor the explanation to the user's question while keeping the same overall structure.

    --------------------------------------------------

    # Short Answer

    Provide a concise 2–4 sentence answer to the user's question.

    --------------------------------------------------

    # Repository Overview

    Explain which parts of the repository are relevant to the question.

    Describe the repository's purpose, major components, and overall context before answering in detail.

    --------------------------------------------------

    # Detailed Explanation

    Provide a thorough engineering explanation.

    When appropriate, explain:

    - HOW the repository works
    - WHY design decisions were made
    - HOW the different components interact
    - HOW technologies work together
    - HOW the architecture supports the repository goals

    Avoid generic explanations.

    Ground everything in repository evidence.

    --------------------------------------------------

    # Repository Architecture

    If architecture is relevant:

    Explain

    - major modules
    - component relationships
    - request flow
    - folder organization
    - architectural patterns

    If architecture is not directly relevant, briefly explain why.

    --------------------------------------------------

    # Technologies Used

    If technologies are relevant:

    Explain

    - programming languages
    - frameworks
    - databases
    - cloud
    - CI/CD
    - containers
    - package managers

    For each important technology explain

    - where it appears
    - why it is used
    - how it interacts with the rest of the repository

    Do NOT simply list technologies.

    --------------------------------------------------

    # Key Repository Evidence

    Provide bullet points using information extracted from the repository analysis.

    Examples:

    - README findings
    - Architecture analysis
    - Repository structure
    - Repository identity
    - Purpose analysis
    - Technology analysis
    - Health analysis
    - Repository DNA
    - Activity metrics

    --------------------------------------------------

    # Interesting Engineering Observations

    Mention observations an experienced software engineer would notice.

    Examples include:

    - architectural strengths
    - scalability
    - maintainability
    - modularity
    - code organization
    - engineering maturity
    - technology choices
    - potential risks
    - interesting implementation decisions

    --------------------------------------------------

    # Conclusion

    Summarize the answer in 2–4 sentences.

    End with the overall engineering assessment relevant to the user's question.
    """

    def build_question_guidance(self, question: str) -> str:
        """
        Build question-specific guidance so Gemini responds
        like an experienced software engineer reviewing the repository.
        """

        text = question.lower()

        common = (
            "IMPORTANT:\n"
            "- Use ONLY the supplied repository analysis.\n"
            "- Never invent technologies, architecture, APIs, or features.\n"
            "- Support every major statement using repository evidence.\n"
            "- Write naturally and professionally.\n"
            "- Unless the user explicitly requests a brief answer, produce approximately 300–800 words.\n"
            "- Do NOT stop after the Short Answer.\n"
            "- Every required section must be completed.\n"
        )

        # ------------------------------------------------------------
        # Repository Overview
        # ------------------------------------------------------------
        if any(term in text for term in [
            "overview",
            "summary",
            "what is this",
            "repository",
            "project",
            "purpose",
            "explain this repository",
        ]):

            return common + """

    Focus on explaining the repository as a whole.

    Include:

    - Short Answer
    - Repository Overview
    - Purpose
    - Target Users
    - Major Features
    - Repository Architecture (high level)
    - Technologies Used
    - Repository Organization
    - Key Repository Evidence
    - Interesting Engineering Observations
    - Conclusion

    Explain HOW the repository works and WHY it exists.
    """

        # ------------------------------------------------------------
        # Architecture
        # ------------------------------------------------------------
        if any(term in text for term in [
            "architecture",
            "design",
            "system",
            "components",
            "module",
            "modules",
            "flow",
            "scalability",
            "maintainability",
        ]):

            return common + """

    Answer as a senior software architect.

    Include:

    - Short Answer
    - Architecture Summary
    - Major Components
    - Module Responsibilities
    - Repository Structure
    - Request / Data Flow
    - Architectural Patterns
    - Technologies Supporting the Architecture
    - Engineering Trade-offs
    - Possible Improvements
    - Conclusion

    Explain WHY the architecture was chosen.
    """

        # ------------------------------------------------------------
        # Technologies
        # ------------------------------------------------------------
        if any(term in text for term in [
            "technology",
            "technologies",
            "framework",
            "frameworks",
            "language",
            "languages",
            "database",
            "cloud",
            "docker",
            "container",
            "ci",
            "cd",
        ]):

            return common + """

    Explain every important technology found in the repository.

    Include:

    - Short Answer
    - Technology Overview
    - Programming Languages
    - Frontend Technologies
    - Backend Technologies
    - Databases
    - Cloud & Infrastructure
    - DevOps / CI/CD
    - Build Tools & Package Managers
    - How the technologies work together
    - Repository Evidence
    - Engineering Observations
    - Conclusion

    Do not simply list technologies.
    Explain WHY each technology exists in the repository.
    """

        # ------------------------------------------------------------
        # Repository Health
        # ------------------------------------------------------------
        if any(term in text for term in [
            "health",
            "quality",
            "maintenance",
            "activity",
            "issues",
            "contributors",
            "releases",
            "maturity",
        ]):

            return common + """

    Evaluate the engineering quality of the repository.

    Include:

    - Short Answer
    - Overall Health
    - Documentation
    - Activity
    - Repository Maturity
    - Strengths
    - Weaknesses
    - Maintainability
    - Recommended Improvements
    - Conclusion

    Support every evaluation using repository evidence.
    """

        # ------------------------------------------------------------
        # README
        # ------------------------------------------------------------
        if any(term in text for term in [
            "readme",
            "documentation",
            "docs",
        ]):

            return common + """

    Evaluate the repository documentation.

    Include:

    - Short Answer
    - Documentation Overview
    - README Coverage
    - Missing Information
    - Ease of Understanding
    - Suggested Improvements
    - Conclusion
    """

        # ------------------------------------------------------------
        # Default
        # ------------------------------------------------------------
        return common + """

    Answer as an experienced software engineer reviewing the repository.

    Include:

    - Short Answer
    - Repository Overview
    - Detailed Explanation
    - Repository Evidence
    - Engineering Observations
    - Conclusion

    Tailor the explanation to the user's question.
    """

    def select_context(self, question: str) -> list[str]:
        """
        Select the most relevant repository context for the user's question.

        Instead of aggressively filtering context, Atlas always provides
        a strong repository foundation and then enriches it with
        question-specific analysis.
        """

        text = question.lower()

        # Always include these sections.
        # They give Gemini enough understanding of the repository before
        # answering any specific question.
        base_context = [
            "summary",
            "purpose",
            "repository_identity",
            "architecture",
            "tech_stack",
        ]

        # Repository overview / introduction
        if any(term in text for term in [
            "overview",
            "summary",
            "what is this",
            "what does this repository do",
            "purpose",
            "who is it for",
            "explain this repository",
            "repository",
            "project",
        ]):
            return base_context + [
                "repository_dna",
                "structure",
                "repository_tree",
                "health",
                "activity",
                "knowledge",
                "blueprint",
                "readme_summary",
            ]

        # Architecture
        if any(term in text for term in [
            "architecture",
            "design",
            "system design",
            "components",
            "module",
            "modules",
            "service",
            "services",
            "scalability",
            "maintainability",
            "clean architecture",
            "design pattern",
            "flow",
        ]):
            return base_context + [
                "structure",
                "repository_tree",
                "repository_dna",
                "knowledge",
                "blueprint",
                "readme_summary",
            ]

        # Technologies
        if any(term in text for term in [
            "technology",
            "technologies",
            "tech stack",
            "framework",
            "frameworks",
            "language",
            "languages",
            "database",
            "cloud",
            "docker",
            "container",
            "deployment",
            "ci",
            "cd",
            "package",
            "dependency",
        ]):
            return base_context + [
                "repository_dna",
                "structure",
                "repository_tree",
                "readme_summary",
                "knowledge",
                "blueprint",
            ]

        # Repository structure
        if any(term in text for term in [
            "folder",
            "directory",
            "tree",
            "structure",
            "layout",
            "entry point",
            "where should i start",
            "important files",
        ]):
            return base_context + [
                "structure",
                "repository_tree",
                "knowledge",
                "blueprint",
                "readme_summary",
            ]

        # Health / maintenance
        if any(term in text for term in [
            "health",
            "quality",
            "maintain",
            "maintenance",
            "activity",
            "contributors",
            "issues",
            "pull requests",
            "pr",
            "releases",
            "maturity",
            "documentation",
        ]):
            return base_context + [
                "health",
                "activity",
                "repository_dna",
                "knowledge",
                "readme_summary",
            ]

        # README / documentation
        if any(term in text for term in [
            "readme",
            "documentation",
            "docs",
            "install",
            "usage",
            "guide",
        ]):
            return base_context + [
                "readme_summary",
                "structure",
                "repository_tree",
                "knowledge",
            ]

        # Default: provide a comprehensive repository view.
        return [
            "summary",
            "purpose",
            "repository_identity",
            "architecture",
            "tech_stack",
            "structure",
            "repository_tree",
            "repository_dna",
            "health",
            "activity",
            "knowledge",
            "blueprint",
            "readme_summary",
        ]
    
    def _extract_context(self, context: str, selected_context: list[str]) -> str:
        if not selected_context:
            return context
        requested = [item.strip() for item in selected_context if item.strip()]
        if "summary" not in requested:
            requested.insert(0, "summary")

        context_sections: list[str] = []
        section_map = {
            "repository_metadata": r"^## Repository Metadata",
            "repository_tree": r"^## Repository Tree",
            "entry_points": r"^## Repository Structure",
            "important_folders": r"^## Repository Structure",
            "configuration_files": r"^## Repository Structure",
            "readme_summary": r"^## README Summary",
            "tech_stack": r"^## Tech Stack",
            "architecture": r"^## Architecture",
            "structure": r"^## Repository Structure",
            "health": r"^## Health and Activity",
            "activity": r"^## Health and Activity",
            "summary": r"^## Repository Summary",
            "purpose": r"^## Purpose",
            "repository_identity": r"^## Repository Identity",
            "repository_dna": r"^## Repository DNA",
            "knowledge": r"^## Knowledge and Blueprint",
            "blueprint": r"^## Knowledge and Blueprint",
        }
        for section_name in ["repository_metadata", *requested]:
            pattern = re.compile(section_map.get(section_name, rf"^## {re.escape(section_name.title())}"), re.MULTILINE)
            match = pattern.search(context)
            if match:
                start = match.start()
                next_section = re.search(r"^## ", context[start + 1 :], re.MULTILINE)
                if next_section:
                    end = start + 1 + next_section.start()
                else:
                    end = len(context)
                context_sections.append(context[start:end].strip())
        if context_sections:
            return "\n\n".join(context_sections)
        return context
    """
    def generate_answer(self, request: ChatRequest) -> ChatResponse:
        prompt = self.build_prompt(request)
        try:
            answer = self.provider.generate(prompt, temperature=float(os.getenv("TEMPERATURE", "0.2")), max_tokens=int(os.getenv("MAX_TOKENS", "1200")))
        except ValueError as exc:
            answer = self._fallback_answer(request.question, str(exc))
        except Exception as exc:
            answer = self._fallback_answer(request.question, str(exc))

        sources = self._collect_sources(request.analysis)
        return ChatResponse(answer=answer, sources=sources)
    """

    def generate_answer(self, request: ChatRequest) -> ChatResponse:
        prompt = self.build_prompt(request)

        try:
            answer = self.provider.generate(
                prompt,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            )
        except Exception as exc:
            answer = self._fallback_answer(request.question, str(exc))

        sources = self._collect_sources(request.analysis)

        return ChatResponse(
            answer=answer,
            sources=sources,
        )

    def _fallback_answer(self, question: str, error: str) -> str:
        if "GEMINI_API_KEY" in error or "configured" in error.lower():
            return (
                "## Configuration Error\n"
                "GEMINI_API_KEY is not configured, so Atlas cannot produce a live repository answer right now.\n\n"
                "## Short Answer\n"
                "The assistant cannot generate a grounded response until the Gemini provider is configured.\n\n"
                "## Detailed Explanation\n"
                "Atlas has the repository analysis available locally, but it cannot call the LLM provider without a valid API key.\n\n"
                "## Recommendations\n"
                "- Configure GEMINI_API_KEY and MODEL_NAME in the backend environment.\n"
                "- Restart the backend and retry your question."
            )
        return (
            "## Short Answer\n"
            "Based on the available repository analysis, I cannot fully answer this request right now because the LLM provider is unavailable.\n\n"
            "## Detailed Explanation\n"
            "The repository context is still available locally, but the assistant needs a configured LLM provider to produce a richer explanation.\n\n"
            "## Recommendations\n"
            "- Configure GEMINI_API_KEY and MODEL_NAME to enable full responses.\n"
            "- Re-run your question once the backend is configured."
        )

    def _collect_sources(self, analysis: dict[str, Any]) -> list[ChatSource]:
        summary = analysis.get("summary") or {}
        architecture = analysis.get("architecture") or {}
        structure = analysis.get("structure") or {}
        tech_stack = analysis.get("tech_stack") or {}
        health = analysis.get("health") or {}
        classification = analysis.get("classification") or {}

        sources: list[ChatSource] = []
        if summary.get("overview"):
            sources.append(ChatSource(title="Repository Summary", kind="summary", snippet=summary["overview"]))
        if architecture.get("summary"):
            sources.append(ChatSource(title="Architecture Analysis", kind="architecture", snippet=architecture["summary"]))
        if structure.get("summary"):
            sources.append(ChatSource(title="Repository Structure", kind="structure", snippet=structure["summary"]))
        if tech_stack.get("frontend") or tech_stack.get("backend"):
            sources.append(ChatSource(title="Tech Stack", kind="tech_stack", snippet="Frontend: " + ", ".join(tech_stack.get("frontend", [])) + " | Backend: " + ", ".join(tech_stack.get("backend", []))))
        if health.get("overall_status"):
            sources.append(ChatSource(title="Health Analysis", kind="health", snippet=f"Overall status: {health['overall_status']}"))
        if classification.get("primary_classification"):
            sources.append(ChatSource(title="Classification", kind="classification", snippet=classification["primary_classification"]))

        return sources[:6]
