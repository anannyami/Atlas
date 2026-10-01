from __future__ import annotations
from core.config import settings
import os
import re
import logging
import time
import hashlib
import json
import threading
from collections import OrderedDict
from concurrent.futures import Future
from typing import Any

from models.chat import ChatRequest, ChatResponse, ChatSource
from services.conversation_state import ConversationState, ConversationStateService
from services.intent_classifier import IntentClassification, IntentClassifier
from services.llm.gemini_provider import GeminiProvider
from services.repository_brief_builder import RepositoryBriefBuilder
from services.repair_prompt_builder import RepairPromptBuilder
from services.response_validator import ResponseValidator


class ChatService:
    """Generate repository-aware answers from Atlas analysis output."""

    RESPONSE_CACHE_TTL_SECONDS = 30 * 60
    RESPONSE_CACHE_MAX_ENTRIES = 256
    ANALYSIS_CACHE_MAX_ENTRIES = 32

    def __init__(self, provider: Any | None = None) -> None:
        self.provider = provider or self._build_provider()
        self.intent_classifier = IntentClassifier()
        self.conversation_state_service = ConversationStateService()
        self.repository_brief_builder = RepositoryBriefBuilder()
        self.repair_prompt_builder = RepairPromptBuilder()
        self.response_validator = ResponseValidator()
        self._cache_lock = threading.RLock()
        self._response_cache: OrderedDict[str, tuple[float, ChatResponse]] = OrderedDict()
        self._inflight_requests: dict[str, Future[ChatResponse]] = {}
        self._brief_cache: OrderedDict[str, str] = OrderedDict()
        self._context_cache: OrderedDict[tuple[str, tuple[str, ...]], str] = OrderedDict()

    def _analysis_fingerprint(self, analysis: dict[str, Any]) -> str:
        serialized = json.dumps(analysis, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _bounded_cache_set(self, cache: OrderedDict, key: Any, value: Any, max_entries: int) -> None:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > max_entries:
            cache.popitem(last=False)

    def _get_repository_brief(self, analysis: dict[str, Any]) -> str:
        fingerprint = self._analysis_fingerprint(analysis)
        with self._cache_lock:
            cached = self._brief_cache.get(fingerprint)
            if cached is not None:
                self._brief_cache.move_to_end(fingerprint)
                return cached
            brief = self.repository_brief_builder.build(analysis)
            self._bounded_cache_set(
                self._brief_cache,
                fingerprint,
                brief,
                self.ANALYSIS_CACHE_MAX_ENTRIES,
            )
            return brief

    def _get_repository_context(
        self,
        analysis: dict[str, Any],
        selected_context: list[str],
    ) -> str:
        fingerprint = self._analysis_fingerprint(analysis)
        key = (fingerprint, tuple(selected_context))
        with self._cache_lock:
            cached = self._context_cache.get(key)
            if cached is not None:
                self._context_cache.move_to_end(key)
                return cached
            context = self.build_context(analysis)
            if selected_context:
                context = self._extract_context(context, selected_context)
            self._bounded_cache_set(
                self._context_cache,
                key,
                context,
                self.ANALYSIS_CACHE_MAX_ENTRIES,
            )
            return context

    def _response_cache_key(self, request: ChatRequest) -> str:
        repository_fingerprint = self._analysis_fingerprint(request.analysis)
        normalized_question = " ".join(request.question.casefold().split()).rstrip("?!.,;:").strip()
        return f"{repository_fingerprint}::{normalized_question}"

    def generate_answer(self, request: ChatRequest) -> ChatResponse:
        cacheable = not bool(request.conversation)
        key = self._response_cache_key(request) if cacheable else None
        now = time.monotonic()
        owner = False
        with self._cache_lock:
            expired = [cache_key for cache_key, (expires, _) in self._response_cache.items() if expires <= now]
            for cache_key in expired:
                self._response_cache.pop(cache_key, None)

            cached = self._response_cache.get(key) if key is not None else None
            if cached is not None:
                self._response_cache.move_to_end(key)
                response = cached[1].model_copy(deep=True)
                if os.getenv("PROMPT_DEBUG", "").lower() in {"1", "true", "yes", "on"}:
                    logging.getLogger(__name__).info(
                        "AI request diagnostics question=%r logical_gemini_calls=0 cache_hit=True total_request_ms=0",
                        request.question[:120],
                    )
                return response

            future = self._inflight_requests.get(key) if key is not None else None
            if future is None:
                future = Future()
                if key is not None:
                    self._inflight_requests[key] = future
                owner = True

        if not owner:
            response = future.result()
            return response.model_copy(deep=True)

        try:
            response = self._generate_answer_uncached(request)
            if key is not None and (response.validation is None or response.validation.passed):
                with self._cache_lock:
                    self._bounded_cache_set(
                        self._response_cache,
                        key,
                        (time.monotonic() + self.RESPONSE_CACHE_TTL_SECONDS, response.model_copy(deep=True)),
                        self.RESPONSE_CACHE_MAX_ENTRIES,
                    )
            future.set_result(response.model_copy(deep=True))
            return response
        except BaseException as exc:
            future.set_exception(exc)
            raise
        finally:
            if key is not None:
                with self._cache_lock:
                    self._inflight_requests.pop(key, None)

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
        purpose = analysis.get("purpose") or {}
        architecture = analysis.get("architecture") or {}
        tech_stack = analysis.get("tech_stack") or {}
        structure = analysis.get("structure") or {}
        knowledge = analysis.get("knowledge") or {}
        blueprint = analysis.get("blueprint") or {}
        repository_identity = analysis.get("repository_identity") or {}
        product_identity = analysis.get("product_identity") or {}
        classification = analysis.get("classification") or {}
        health = analysis.get("health") or {}
        activity = analysis.get("activity") or {}

        def add_field(lines: list[str], label: str, value: Any) -> None:
            if value is not None and value != "" and value != [] and value != {}:
                lines.append(f"- {label}: {self._normalise_text(value)}")

        def add_signals(lines: list[str], label: str, values: Any) -> None:
            signals = [item for item in (values or []) if isinstance(item, dict) and item.get("name")]
            if signals:
                details = []
                for item in signals:
                    evidence = self._join(item.get("evidence") or [])
                    signal = f"{item['name']} (confidence: {item.get('confidence', 'unspecified')})"
                    if evidence != "Unavailable":
                        signal += f"; evidence: {evidence}"
                    details.append(signal)
                lines.append(f"- {label}: " + " | ".join(details))

        def append_section(title: str, lines: list[str]) -> None:
            if lines:
                sections.append(self._build_section(title, lines))

        sections: list[str] = []

        identity_lines: list[str] = []
        add_field(identity_lines, "Repository", repository.get("full_name") or repository.get("name"))
        add_field(identity_lines, "Owner", repository.get("owner"))
        add_field(identity_lines, "Description", repository.get("description"))
        add_field(identity_lines, "Product", product_identity.get("title") or repository_identity.get("product_name"))
        add_field(identity_lines, "Category", product_identity.get("category") or repository_identity.get("category"))
        add_field(identity_lines, "Tagline", repository_identity.get("tagline"))
        add_field(identity_lines, "Topics", repository.get("topics"))
        add_field(identity_lines, "Product evidence", product_identity.get("evidence"))
        append_section("Repository Identity", identity_lines)

        purpose_lines: list[str] = []
        add_field(purpose_lines, "Overview", summary.get("overview"))
        add_field(purpose_lines, "What it does", purpose.get("what"))
        add_field(purpose_lines, "Why it exists", purpose.get("why") or summary.get("purpose"))
        add_field(purpose_lines, "Audience", purpose.get("audience") or repository_identity.get("audience"))
        add_field(purpose_lines, "Problem addressed", purpose.get("problem"))
        add_field(purpose_lines, "Capabilities", purpose.get("capabilities") or repository_identity.get("capabilities"))
        add_field(purpose_lines, "Technology rationale", purpose.get("technology_story"))
        add_field(purpose_lines, "Classification", classification.get("primary_classification") or classification.get("project_type"))
        append_section("Repository Purpose", purpose_lines)

        architecture_lines: list[str] = []
        add_field(architecture_lines, "Style", architecture.get("style"))
        add_field(architecture_lines, "Summary", architecture.get("summary"))
        add_field(architecture_lines, "Confidence", architecture.get("confidence"))
        add_field(architecture_lines, "Applications", architecture.get("applications"))
        add_field(architecture_lines, "Workspace", architecture.get("workspace"))
        add_field(architecture_lines, "Modules", architecture.get("modules"))
        add_field(architecture_lines, "Organization", architecture.get("organization"))
        add_field(architecture_lines, "Deployment signals", architecture.get("deployment"))
        for key, label in (
            ("architecture_patterns", "Patterns"),
            ("api_styles", "API styles"),
            ("authentication", "Authentication signals"),
            ("frontend_frameworks", "Frontend frameworks"),
            ("backend_frameworks", "Backend frameworks"),
            ("databases", "Database signals"),
            ("cloud", "Cloud signals"),
        ):
            add_signals(architecture_lines, label, architecture.get(key))
        append_section("Architecture", architecture_lines)

        technology_lines: list[str] = []
        for key, label in (
            ("languages", "Languages"),
            ("frontend", "Frontend"),
            ("backend", "Backend"),
            ("database", "Data stores and database libraries"),
            ("cloud", "Cloud"),
            ("ci_cd", "CI/CD"),
            ("package_managers", "Package managers"),
            ("containers", "Containers"),
            ("mobile", "Mobile"),
        ):
            add_field(technology_lines, label, tech_stack.get(key))
        add_signals(technology_lines, "Detected technologies with evidence", tech_stack.get("technologies"))
        append_section("Technology Stack", technology_lines)

        structure_lines: list[str] = []
        add_field(structure_lines, "Summary", structure.get("summary"))
        add_field(structure_lines, "File and directory counts", {
            "files": structure.get("total_files"),
            "directories": structure.get("total_directories"),
            "maximum depth": structure.get("max_depth"),
        })
        add_field(structure_lines, "Major directories", structure.get("major_directories"))
        add_field(structure_lines, "Major modules", structure.get("major_modules"))
        add_field(structure_lines, "Entry points", structure.get("entry_points"))
        add_field(structure_lines, "Important folders", structure.get("important_folders"))
        add_field(structure_lines, "Configuration files", structure.get("configuration_files"))
        add_field(structure_lines, "Largest directories", structure.get("largest_directories"))
        add_field(structure_lines, "Deepest paths", structure.get("deepest_paths"))
        append_section("Repository Structure", structure_lines)

        tree = analysis.get("repository_tree") or knowledge.get("tree") or []
        if tree:
            tree_lines: list[str] = []
            tree_queue = [(node, 0) for node in tree if isinstance(node, dict)]
            queue_index = 0
            while queue_index < len(tree_queue) and len(tree_lines) < 48:
                node, depth = tree_queue[queue_index]
                queue_index += 1
                name = node.get("name") or node.get("path")
                path = node.get("path")
                tree_lines.append("  " * depth + f"- {name}" + (f" ({path})" if path and path != name else ""))
                children = node.get("children") or []
                if depth < 2:
                    tree_queue.extend((child, depth + 1) for child in children[:48] if isinstance(child, dict))
            if tree_lines:
                if queue_index < len(tree_queue):
                    tree_lines.append("- Additional tree entries omitted from this outline.")
                append_section("Repository Tree Highlights", tree_lines)

        knowledge_lines: list[str] = []
        add_field(knowledge_lines, "Capabilities", knowledge.get("capabilities"))
        add_field(knowledge_lines, "Major folders", knowledge.get("major_folders"))
        add_field(knowledge_lines, "Dependencies", knowledge.get("dependencies"))
        evidence = knowledge.get("evidence") or []
        if evidence:
            evidence_lines = []
            for item in evidence[:12]:
                if isinstance(item, dict):
                    source = item.get("source")
                    details = item.get("details")
                    if source or details:
                        evidence_lines.append(f"{source or 'Evidence'}: {details or ''}".strip())
            add_field(knowledge_lines, "Evidence", evidence_lines)
        if blueprint:
            add_field(knowledge_lines, "Blueprint architecture type", blueprint.get("architecture_type"))
            add_field(knowledge_lines, "Blueprint confidence", blueprint.get("confidence"))
            for key, label in (
                ("layers", "Blueprint layers"),
                ("components", "Blueprint components"),
                ("dependencies", "Blueprint dependencies"),
                ("communication", "Communication paths"),
                ("entrypoints", "Blueprint entry points"),
                ("external_services", "External services"),
                ("data_flow", "Data flow"),
            ):
                add_field(knowledge_lines, label, blueprint.get(key))
        readme = knowledge.get("readme")
        if isinstance(readme, str) and readme.strip():
            excerpt = readme.strip()
            if len(excerpt) > 1600:
                excerpt = excerpt[:1597].rstrip() + "..."
            add_field(knowledge_lines, "README excerpt", excerpt)
        append_section("Repository Knowledge", knowledge_lines)

        observation_lines: list[str] = []
        add_field(observation_lines, "Summary highlights", summary.get("highlights"))
        add_field(observation_lines, "Repository identity evidence", repository_identity.get("evidence"))
        add_field(observation_lines, "Product identity confidence", product_identity.get("confidence"))
        secondary_classifications = classification.get("secondary_classifications") or []
        add_signals(observation_lines, "Secondary classifications", secondary_classifications)
        append_section("Engineering Observations", observation_lines)

        health_lines: list[str] = []
        add_field(health_lines, "Score", health.get("score"))
        add_field(health_lines, "Overall status", health.get("overall_status"))
        add_field(health_lines, "Component scores", health.get("component_scores"))
        add_field(health_lines, "Checks", health.get("checks"))
        add_field(health_lines, "Recommendations", health.get("missing_recommendations"))
        append_section("Repository Health", health_lines)

        activity_lines: list[str] = []
        for key, label in (
            ("activity_level", "Activity level"),
            ("maintenance_status", "Maintenance status"),
            ("repository_maturity", "Repository maturity"),
            ("last_commit_days", "Days since last commit"),
            ("recent_commits", "Recent commits in fetched sample"),
            ("recent_pull_requests", "Pull requests across all states"),
            ("recent_issues", "Open issues excluding pull requests"),
            ("observed_samples", "Observed samples"),
            ("releases", "Releases"),
            ("stars", "Stars"),
            ("forks", "Forks"),
            ("open_issues", "Open issues"),
            ("staleness", "Staleness"),
        ):
            add_field(activity_lines, label, activity.get(key))
        add_field(activity_lines, "Activity interpretation", activity.get("explanations"))
        append_section("Repository Activity", activity_lines)

        return "\n".join(sections)

    def build_prompt(
        self,
        request: ChatRequest,
        intent_classification: IntentClassification,
        conversation_state: ConversationState,
        repository_brief: str,
    ) -> str:
        question = request.question
        conversation = list(request.conversation or [])
        if (
            conversation
            and conversation[-1].role.lower() == "user"
            and conversation[-1].content.strip() == question.strip()
        ):
            conversation.pop()

        selected_context = self.select_context(
            question,
            intent_classification,
            conversation_state,
        )
        selected_context_text = ", ".join(selected_context) if selected_context else "Full repository analysis"

        context = self._get_repository_context(request.analysis, selected_context)

        redundant_brief_labels: set[str] = set()
        if {"summary", "purpose"} & set(selected_context):
            redundant_brief_labels.add("Repository Purpose")
        if "architecture" in selected_context:
            redundant_brief_labels.update({"Architecture Summary", "Engineering Style"})
        if "tech_stack" in selected_context:
            redundant_brief_labels.add("Technology Overview")
        if "structure" in selected_context:
            redundant_brief_labels.update({"Repository Organization", "Important Components"})
        if "activity" in selected_context:
            redundant_brief_labels.update({"Engineering Maturity", "Key Engineering Observations"})
        if {"repository_identity", "product_identity"} & set(selected_context):
            redundant_brief_labels.add("Repository Identity")
        repository_brief = "\n".join(
            line
            for line in repository_brief.splitlines()
            if not any(line.startswith(f"{label}:") for label in redundant_brief_labels)
        )

        intent_labels = {
            "repository_overview": "repository overview",
            "architecture": "architecture",
            "technology": "technology choices",
            "folder_structure": "folder structure",
            "repository_tree": "repository tree",
            "security": "security",
            "performance": "performance",
            "health": "repository health",
            "documentation": "documentation",
            "deployment": "deployment",
            "devops": "DevOps practices",
            "scalability": "scalability",
            "comparison": "comparison",
            "improvement_suggestions": "improvement suggestions",
            "code_explanation": "code explanation",
            "follow_up": "follow-up question",
            "general_repository_question": "general repository understanding",
        }
        current_intents = [intent_labels.get(intent.value, intent.value.replace("_", " ")) for intent in intent_classification.intents]
        contextual_intents = [intent_labels.get(intent.value, intent.value.replace("_", " ")) for intent in intent_classification.contextual_intents]

        area_guidance = {
            "repository overview": "purpose, summary, identity, and classification",
            "architecture": "architecture, structure, and blueprint evidence",
            "technology choices": "technology stack and architecture evidence",
            "folder structure": "structure and repository tree evidence",
            "repository tree": "repository tree and structure evidence",
            "security": "security-related architecture and available authentication evidence",
            "performance": "architecture, technology, and available activity evidence",
            "repository health": "health, activity, and maintenance evidence",
            "documentation": "README and available knowledge evidence",
            "deployment": "deployment, infrastructure, and technology evidence",
            "DevOps practices": "CI/CD, containers, and repository organization evidence",
            "scalability": "architecture, technology, and activity evidence",
            "comparison": "the repository evidence relevant to each comparison dimension",
            "improvement suggestions": "health, structure, architecture, and documented evidence",
            "code explanation": "relevant architecture, structure, and knowledge evidence",
            "follow-up question": "the current component and topics already discussed",
            "general repository understanding": "summary, purpose, architecture, and technology evidence",
        }
        emphasized_intents = list(dict.fromkeys([*current_intents, *contextual_intents]))
        emphasis = "; ".join(
            f"{intent}: prioritize {area_guidance.get(intent, 'directly relevant repository evidence')}"
            for intent in emphasized_intents
        ) or "Use the repository evidence most directly relevant to the question."
        follow_up_description = (
            "This continues an earlier discussion; preserve continuity."
            if intent_classification.is_follow_up
            else "Treat this as a new question unless the conversation state indicates an established topic."
        )
        intent_instructions = (
            f"The user is asking about {', '.join(current_intents) or 'the repository'}. "
            f"Answer from the engineering perspective appropriate to those intents. {follow_up_description}\n"
            f"Repository areas to emphasize: {emphasis}"
        )

        def state_value(value: str | None) -> str:
            return value if value else "None recorded."

        def state_list(values: list[str]) -> str:
            return ", ".join(values) if values else "None recorded."

        recent_turn_summaries = []
        for message in conversation[-6:]:
            compact_content = re.sub(r"[#*_`>]", "", message.content)
            compact_content = re.sub(r"\s+", " ", compact_content).strip()
            if len(compact_content) > 180:
                compact_content = compact_content[:177].rstrip() + "..."
            speaker = "User asked" if message.role.lower() == "user" else "Assistant response summary"
            recent_turn_summaries.append(f"- {speaker}: {compact_content}")
        recent_history_summary = "\n".join(recent_turn_summaries) or "No earlier turns in this request."

        conversation_state_lines = [
            f"Current Topic: {state_value(conversation_state.current_topic)}",
            f"Current Component: {state_value(conversation_state.current_component)}",
            f"Previously Discussed Topics: {state_list(conversation_state.discussed_topics)}",
            f"Pending Topics: {state_list(conversation_state.pending_topics)}",
            f"User-Mentioned Technologies (conversational references, not verified repository facts): {state_list(conversation_state.mentioned_technologies)}",
            f"Mentioned Components: {state_list(conversation_state.mentioned_components)}",
            f"Recent Conversation Summary:\n{recent_history_summary}",
        ]
        if conversation_state.current_user_goal and conversation_state.current_user_goal.strip() != question.strip():
            conversation_state_lines.insert(2, f"Current User Goal: {conversation_state.current_user_goal}")
        if conversation_state.last_user_question and conversation_state.last_user_question.strip() != question.strip():
            conversation_state_lines.insert(-1, f"Last User Question: {conversation_state.last_user_question}")
        conversation_state_text = "\n".join(conversation_state_lines)

        return f"""{self.build_system_prompt()}

Intent Classification
=====================
{intent_instructions}

Conversation State
==================
{conversation_state_text}

Repository Brief
================
{repository_brief}

Relevant Repository Context
===========================
{context}

{self.build_question_guidance(question, intent_classification, conversation_state)}

User Question:
{question}

{self.build_response_template()}
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
        """Return the mandatory response structure and evidence constraints."""
        return """
RESPONSE CONTRACT

Use repository evidence supplied in the prompt; do not invent repository facts. Distinguish observed facts from implications, and state evidence gaps plainly. Unless brevity is requested or evidence is limited, target 300–800 words. Complete each heading concisely; mark irrelevant headings briefly.

# Short Answer
Answer directly in 2–4 sentences.

# Repository Overview
Give only the context needed for this question; do not repeat the full summary.

# Detailed Explanation
Explain engineering reasoning, interactions, and tradeoffs when supported. Synthesize relevant analysis areas rather than describing only one.

# Repository Evidence
Give concise, specific evidence for key claims and identify its analysis area when available. Cite only supplied evidence.

# Engineering Observations
Give relevant evidence-backed strengths, limitations, risks, or improvements. Label uncertainty; do not treat heuristics or partial samples as proof.

# Conclusion
Close with a short answer-specific takeaway; add no new claims.

For follow-ups, continue the established topic and avoid repeating prior explanations. Conversation state is continuity context, not repository evidence.
"""

    def build_question_guidance(
        self,
        question: str,
        intent_classification: IntentClassification,
        conversation_state: ConversationState,
    ) -> str:
        """Guide reasoning using classified intent and conversational state only."""
        text = question.lower()
        intent_values = {intent.value for intent in intent_classification.intents}

        guidance_by_intent = {
            "repository_overview": "Explain the repository at a high level, connecting purpose, identity, classification, major areas, and evidence without repeating the full brief.",
            "architecture": "Explain the observed architecture, component responsibilities and interactions, request or data flow where evidenced, design rationale, scalability implications, and tradeoffs. Separate observed facts from evaluation.",
            "technology": "Explain why each relevant detected technology appears to be used, how technologies interact, and evidence-backed strengths and limitations. Do not infer usage from a technology name alone.",
            "folder_structure": "Explain how the relevant folders and entry points are organized and what responsibilities the available structure supports; distinguish path evidence from inferred roles.",
            "repository_tree": "Use the supplied tree and structure evidence to orient the explanation around the relevant paths; do not claim file contents that were not supplied.",
            "security": "Review only security signals present in the repository analysis. Distinguish detected authentication or security evidence from unverified controls and identify evidence gaps explicitly.",
            "performance": "Assess performance implications only where architecture, technology, or activity evidence supports them. State what cannot be concluded without runtime or workload measurements.",
            "health": "Evaluate repository health using the supplied checks, scores, recommendations, maturity, and activity evidence; explain risks without treating heuristic scores as proof of code quality.",
            "documentation": "Assess the available README and documentation evidence, including what it covers and what is not represented in the supplied analysis; do not invent missing sections.",
            "deployment": "Explain deployment signals and their relationship to architecture and technologies. Do not assume a production topology beyond the repository evidence.",
            "devops": "Discuss detected CI/CD, container, and infrastructure signals and how they relate to engineering workflow; do not infer pipeline behavior that is not evidenced.",
            "scalability": "Assess scalability from architecture and technology evidence, identify likely constraints as hypotheses, and clearly state that capacity requires workload and runtime evidence.",
            "comparison": "Compare the requested alternatives on explicit dimensions such as architecture, technology, and engineering tradeoffs. Keep repository-side claims evidence-based and label general comparison criteria as general, not repository facts.",
            "improvement_suggestions": "Prioritize actionable improvements tied to observed health, structure, architecture, or documentation evidence. Explain impact and uncertainty; avoid generic recommendations unsupported by this repository.",
            "code_explanation": "Explain only the implementation evidence supplied in the analysis. Use structure and architecture to orient the answer, and say when source-level behavior cannot be determined.",
        }

        guides = [
            guidance_by_intent[intent]
            for intent in intent_values
            if intent in guidance_by_intent
        ]

        if any(term in text for term in ("purpose", "why does", "why was", "who is it for", "audience")):
            guides.append("For repository purpose, distinguish documented purpose from analyzer interpretation and connect audience or problem statements only when supplied as evidence.")
        if any(term in text for term in ("activity", "contributors", "commits", "pull requests", "releases", "maintenance")):
            guides.append("For repository activity, explain sample-window and recency limits; do not infer contributor patterns or repository-wide rates from partial counts.")
        if any(term in text for term in ("identity", "product name", "product identity", "what is atlas")):
            guides.append("For repository or product identity, use supplied identity fields and evidence; distinguish declared README/metadata identity from inferred classification.")
        if any(term in text for term in ("code quality", "code quality", "quality", "maintainability", "weakness", "weaknesses")):
            guides.append("For code quality and engineering improvements, separate repository-level signals from source-level quality claims and tie each risk to concrete supplied evidence.")

        continuity: list[str] = []
        if intent_classification.is_follow_up:
            continuity.append("Treat this as a continuation of the existing engineering discussion and resolve references using the state below.")
        if conversation_state.current_topic or conversation_state.current_component or conversation_state.current_user_goal:
            continuity.append("Use the conversation state above to resolve references and continue the established topic/component.")
        if conversation_state.discussed_topics:
            continuity.append("Build on previously discussed topics and avoid restating their explanations unless needed.")
        if conversation_state.pending_topics:
            continuity.append("Address a pending topic only when it is relevant to the current question.")

        if "follow_up" in intent_values:
            guides.append("Answer the current question directly, resolve short references from conversational continuity, and add only the explanation needed to advance the discussion.")

        common = (
            "Ground repository-specific claims in supplied evidence; label inference and unknowns. "
            "Conversation state provides continuity, never repository facts. Avoid repeating prior material."
        )
        body = "\n".join(f"- {guide}" for guide in dict.fromkeys(guides))
        continuity_text = "\n".join(f"- {item}" for item in continuity)

        return (
            f"Question-specific reasoning guidance\n{common}\n"
            f"{body or '- Answer as an experienced repository engineer, grounding conclusions in supplied analysis.'}\n"
            f"Conversational continuity:\n{continuity_text or '- No additional continuity guidance.'}"
        )

    def select_context(
        self,
        question: str,
        intent_classification: IntentClassification,
        conversation_state: ConversationState,
    ) -> list[str]:
        """
        Rank repository sections using the classified intent and discussion state.
        """
        from services.intent_classifier import Intent

        text = question.lower()
        intent_weights = {
            Intent.REPOSITORY_OVERVIEW: {
                "summary": 8, "purpose": 8, "repository_identity": 6,
                "product_identity": 5, "classification": 4, "structure": 3,
                "tech_stack": 3, "readme_summary": 3, "knowledge": 2,
            },
            Intent.ARCHITECTURE: {
                "architecture": 10, "blueprint": 9, "repository_tree": 8,
                "structure": 8, "tech_stack": 5, "knowledge": 4,
            },
            Intent.TECHNOLOGY: {
                "tech_stack": 10, "purpose": 6, "readme_summary": 6,
                "architecture": 5, "knowledge": 4,
            },
            Intent.FOLDER_STRUCTURE: {
                "structure": 10, "repository_tree": 9, "knowledge": 5,
                "architecture": 3,
            },
            Intent.REPOSITORY_TREE: {
                "repository_tree": 10, "structure": 8, "knowledge": 4,
            },
            Intent.SECURITY: {
                "architecture": 8, "knowledge": 7, "tech_stack": 5,
                "readme_summary": 3,
            },
            Intent.PERFORMANCE: {
                "architecture": 8, "tech_stack": 7, "activity": 6,
                "health": 4, "blueprint": 3,
            },
            Intent.HEALTH: {
                "health": 10, "activity": 9, "classification": 5,
                "repository_identity": 3,
            },
            Intent.DOCUMENTATION: {
                "readme_summary": 10, "knowledge": 7, "structure": 4,
                "purpose": 3,
            },
            Intent.DEPLOYMENT: {
                "architecture": 8, "tech_stack": 7, "structure": 5,
                "blueprint": 4,
            },
            Intent.DEVOPS: {
                "tech_stack": 8, "structure": 6, "health": 5,
                "activity": 3,
            },
            Intent.SCALABILITY: {
                "architecture": 10, "tech_stack": 7, "activity": 6,
                "blueprint": 5, "health": 3,
            },
            Intent.COMPARISON: {
                "architecture": 8, "tech_stack": 8, "purpose": 7,
                "classification": 5, "repository_identity": 3,
            },
            Intent.IMPROVEMENT_SUGGESTIONS: {
                "health": 8, "architecture": 7, "structure": 6,
                "activity": 5, "tech_stack": 4,
            },
            Intent.CODE_EXPLANATION: {
                "structure": 9, "knowledge": 8, "repository_tree": 7,
                "architecture": 6, "tech_stack": 4,
            },
            Intent.FOLLOW_UP: {},
            Intent.GENERAL_REPOSITORY_QUESTION: {
                "summary": 5, "purpose": 5, "architecture": 3,
                "tech_stack": 3, "repository_identity": 2,
            },
        }

        scores = {
            "summary": 1,
            "purpose": 1,
            "architecture": 1,
            "tech_stack": 1,
        }
        ranked_intents = list(dict.fromkeys([
            *intent_classification.intents,
            *intent_classification.contextual_intents,
            *conversation_state.current_intents,
        ]))
        for intent in ranked_intents:
            for section, weight in intent_weights.get(intent, {}).items():
                scores[section] = scores.get(section, 0) + weight

        current_topic = next((
            intent
            for intent in Intent
            if conversation_state.current_topic
            and intent.value.replace("_", " ") == conversation_state.current_topic.lower()
        ), None)
        if current_topic is not None:
            for section, weight in intent_weights.get(current_topic, {}).items():
                scores[section] = scores.get(section, 0) + max(1, weight // 2)

        component_weights = {
            "backend": {"architecture": 3, "tech_stack": 3, "structure": 3, "repository_tree": 2, "knowledge": 2},
            "frontend": {"architecture": 3, "tech_stack": 3, "structure": 3, "repository_tree": 2},
            "api": {"architecture": 3, "tech_stack": 2, "structure": 2, "knowledge": 2},
            "service": {"architecture": 3, "structure": 3, "repository_tree": 2, "knowledge": 2},
            "module": {"architecture": 3, "structure": 3, "repository_tree": 2},
            "repository": {"summary": 3, "purpose": 3, "repository_identity": 2, "classification": 2},
        }
        for component, section_weights in component_weights.items():
            state_component_match = bool(
                conversation_state.current_component
                and re.search(rf"\b{component}\b", conversation_state.current_component, re.IGNORECASE)
            )
            if re.search(rf"\b{component}\b", text) or state_component_match:
                for section, weight in section_weights.items():
                    scores[section] = scores.get(section, 0) + weight

        if intent_classification.is_follow_up:
            scores["summary"] = scores.get("summary", 0) + 1
            scores["purpose"] = scores.get("purpose", 0) + 1
            for intent in intent_classification.contextual_intents:
                for section, weight in intent_weights.get(intent, {}).items():
                    scores[section] = scores.get(section, 0) + max(1, weight // 2)

        section_order = [
            "summary", "purpose", "architecture", "tech_stack", "structure",
            "repository_tree", "knowledge", "blueprint", "repository_identity",
            "product_identity", "health", "activity", "classification",
            "readme_summary",
        ]
        ranked_sections = sorted(
            (section for section in section_order if scores.get(section, 0) > 0),
            key=lambda section: (-scores[section], section_order.index(section), section),
        )

        return ranked_sections[:8]
    
    def _extract_context(self, context: str, selected_context: list[str]) -> str:
        if not selected_context:
            return context
        section_map = {
            "summary": ("Repository Purpose",),
            "purpose": ("Repository Purpose",),
            "repository_metadata": ("Repository Identity",),
            "repository_identity": ("Repository Identity",),
            "product_identity": ("Repository Identity",),
            "architecture": ("Architecture",),
            "tech_stack": ("Technology Stack",),
            "structure": ("Repository Structure",),
            "entry_points": ("Repository Structure",),
            "important_folders": ("Repository Structure",),
            "configuration_files": ("Repository Structure",),
            "repository_tree": ("Repository Tree Highlights",),
            "knowledge": ("Repository Knowledge",),
            "blueprint": ("Repository Knowledge",),
            "readme_summary": ("Repository Knowledge",),
            "health": ("Repository Health",),
            "activity": ("Repository Activity",),
            "classification": ("Repository Purpose", "Engineering Observations"),
            "repository_dna": ("Engineering Observations",),
        }

        heading_matches = list(re.finditer(r"^## (.+)$", context, re.MULTILINE))
        available_sections: dict[str, str] = {}
        for index, match in enumerate(heading_matches):
            end = heading_matches[index + 1].start() if index + 1 < len(heading_matches) else len(context)
            available_sections[match.group(1).strip()] = context[match.start():end].strip()

        selected_sections: list[str] = []
        seen_headings: set[str] = set()
        for section_name in selected_context:
            for heading in section_map.get(section_name, ()):
                section = available_sections.get(heading)
                if section and heading not in seen_headings:
                    selected_sections.append(section)
                    seen_headings.add(heading)

        return "\n\n".join(selected_sections) if selected_sections else context
    """
    def _generate_answer_uncached(self, request: ChatRequest) -> ChatResponse:
        prompt = self.build_prompt(
            request,
            intent_classification,
            conversation_state,
            repository_brief,
        )
        try:
            answer = self.provider.generate(prompt, temperature=float(os.getenv("TEMPERATURE", "0.2")), max_tokens=int(os.getenv("MAX_TOKENS", "1200")))
        except ValueError as exc:
            answer = self._fallback_answer(request.question, str(exc))
        except Exception as exc:
            answer = self._fallback_answer(request.question, str(exc))

        sources = self._collect_sources(request.analysis)
        return ChatResponse(answer=answer, sources=sources)
    """

    def _generate_answer_uncached(self, request: ChatRequest) -> ChatResponse:
        request_started = time.perf_counter()
        prompt_debug = os.getenv("PROMPT_DEBUG", "").lower() in {"1", "true", "yes", "on"}
        logger = logging.getLogger(__name__)
        logical_gemini_calls = 0
        response_generation_seconds = 0.0
        validation_seconds = 0.0
        repair_seconds = 0.0

        def prompt_size(prompt_text: str) -> tuple[int, int, int]:
            characters = len(prompt_text)
            words = len(prompt_text.split())
            return characters, words, round(characters / 4)

        def log_prompt_breakdown(prompt_text: str) -> None:
            markers = (
                ("System Prompt", "You are Atlas"),
                ("Intent Guidance", "Intent Classification\n====================="),
                ("Conversation State", "Conversation State\n=================="),
                ("Conversation Summary", "Recent Conversation Summary:\n"),
                ("Repository Brief", "Repository Brief\n================"),
                ("Repository Context", "Relevant Repository Context\n==========================="),
                ("Question Guidance", "Question-specific reasoning guidance"),
                ("Current User Question", "User Question:\n"),
                ("Response Contract", "RESPONSE CONTRACT"),
            )
            positions = [prompt_text.find(marker) for _, marker in markers]
            total_characters = max(len(prompt_text), 1)
            for index, (name, _) in enumerate(markers):
                start = positions[index]
                if start < 0:
                    continue
                end = positions[index + 1] if index + 1 < len(positions) and positions[index + 1] >= start else len(prompt_text)
                section = prompt_text[start:end]
                chars, words, estimated_tokens = prompt_size(section)
                logger.info(
                    "Prompt section request_question=%r section=%s characters=%d words=%d "
                    "estimated_tokens=%d percent=%.1f",
                    request.question[:120],
                    name,
                    chars,
                    words,
                    estimated_tokens,
                    chars * 100 / total_characters,
                )

        recent_user_messages = [
            message.content
            for message in (request.conversation or [])
            if message.role.lower() == "user"
        ]
        if recent_user_messages and recent_user_messages[-1].strip() == request.question.strip():
            recent_user_messages.pop()
        recent_user_messages = recent_user_messages[-6:]

        conversation_state = None
        earlier_user_messages: list[str] = []
        for previous_question in recent_user_messages:
            previous_classification = self.intent_classifier.classify(
                previous_question,
                recent_user_messages=earlier_user_messages,
            )
            conversation_state = self.conversation_state_service.update(
                state=conversation_state,
                question=previous_question,
                classification=previous_classification,
            )
            earlier_user_messages.append(previous_question)

        intent_classification = self.intent_classifier.classify(
            request.question,
            recent_user_messages=recent_user_messages,
        )
        conversation_state = self.conversation_state_service.update(
            state=conversation_state,
            question=request.question,
            classification=intent_classification,
        )
        repository_brief = self._get_repository_brief(request.analysis)

        prompt = self.build_prompt(
            request,
            intent_classification,
            conversation_state,
            repository_brief,
        )
        prompt_characters, prompt_words, estimated_input_tokens = prompt_size(prompt)
        if prompt_debug:
            log_prompt_breakdown(prompt)
            context_match = re.search(
                r"Relevant Repository Context\n=+\n(.*?)(?=\n\nQuestion-specific reasoning guidance)",
                prompt,
                re.DOTALL,
            )
            context_headings = (
                re.findall(r"^## (.+)$", context_match.group(1), re.MULTILINE)
                if context_match
                else []
            )
            logger.info(
                "Prompt retrieval request_question=%r included_context_sections=%s",
                request.question[:120],
                context_headings,
            )

        generation_succeeded = False
        logical_gemini_calls += 1
        if prompt_debug:
            logger.info(
                "Gemini call start question=%r call_number=%d type=answer prompt_characters=%d "
                "prompt_words=%d estimated_input_tokens=%d",
                request.question[:120],
                logical_gemini_calls,
                prompt_characters,
                prompt_words,
                estimated_input_tokens,
            )
        generation_started = time.perf_counter()
        try:
            answer = self.provider.generate(
                prompt,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            )
            generation_succeeded = True
        except Exception as exc:
            answer = self._fallback_answer(request.question, str(exc))
        response_generation_seconds += time.perf_counter() - generation_started
        initial_answer_chars, initial_answer_words, initial_output_tokens = prompt_size(answer)

        validation_started = time.perf_counter()
        prior_assistant_responses = [
            message.content
            for message in (request.conversation or [])
            if message.role.lower() == "assistant"
        ]
        validation = self.response_validator.validate(
            answer,
            request.analysis,
            request.question,
            is_follow_up=intent_classification.is_follow_up,
            conversation_state=conversation_state.model_dump(),
            prior_assistant_responses=prior_assistant_responses,
        )
        first_validation_seconds = time.perf_counter() - validation_started
        validation_seconds += first_validation_seconds
        original_validation = validation
        retry_triggered = False
        second_validation_score: float | None = None
        repair_generation_seconds = 0.0
        repair_validation_seconds = 0.0
        repair_output_tokens = 0
        repair_reasons = list(validation.issues)
        repair_reasons.extend(validation.missing_sections)
        repair_reasons.extend(validation.missing_repository_evidence)
        repair_reasons.extend(validation.missing_engineering_observations)

        major_validation_failure = (
            bool(validation.missing_sections)
            or bool(validation.missing_repository_evidence)
            or validation.generic_reasoning
            or validation.hallucination_risk >= 0.5
            or (
                validation.category_scores.get("repository_specificity", 1.0) < 0.25
                and validation.category_scores.get("repository_evidence", 1.0) < 0.5
            )
        )

        if generation_succeeded and major_validation_failure:
            retry_triggered = True
            repair_started = time.perf_counter()
            repair_prompt = self.repair_prompt_builder.build(
                original_response=answer,
                validation_result=validation,
                question=request.question,
                repository_analysis=request.analysis,
            )
            repair_prompt_characters, repair_prompt_words, repair_input_tokens = prompt_size(repair_prompt)
            logical_gemini_calls += 1
            if prompt_debug:
                logger.info(
                    "Gemini call start question=%r call_number=%d type=repair prompt_characters=%d "
                    "prompt_words=%d estimated_input_tokens=%d",
                    request.question[:120],
                    logical_gemini_calls,
                    repair_prompt_characters,
                    repair_prompt_words,
                    repair_input_tokens,
                )
            repair_generation_started = time.perf_counter()
            try:
                repaired_answer = self.provider.generate(
                    repair_prompt,
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS,
                )
            except Exception as exc:
                repaired_answer = None
                if os.getenv("PROMPT_DEBUG", "").lower() in {"1", "true", "yes", "on"}:
                    logging.getLogger(__name__).warning(
                        "Response repair attempt failed: %s",
                        type(exc).__name__,
                    )
            repair_generation_seconds = time.perf_counter() - repair_generation_started
            response_generation_seconds += repair_generation_seconds

            if repaired_answer is not None:
                repaired_answer_chars, repaired_answer_words, repair_output_tokens = prompt_size(repaired_answer)
                repair_validation_started = time.perf_counter()
                repaired_validation = self.response_validator.validate(
                    repaired_answer,
                    request.analysis,
                    request.question,
                    is_follow_up=intent_classification.is_follow_up,
                    conversation_state=conversation_state.model_dump(),
                    prior_assistant_responses=prior_assistant_responses,
                )
                repair_validation_seconds = time.perf_counter() - repair_validation_started
                validation_seconds += repair_validation_seconds
                answer = repaired_answer
                validation = repaired_validation
                second_validation_score = repaired_validation.overall_score
            else:
                repaired_answer_chars = 0
                repaired_answer_words = 0
                repair_input_tokens = 0
            repair_seconds = time.perf_counter() - repair_started
        else:
            repair_prompt_characters = 0
            repair_prompt_words = 0
            repair_input_tokens = 0
            repaired_answer_chars = 0
            repaired_answer_words = 0

        final_answer_chars, final_answer_words, final_output_tokens = prompt_size(answer)
        total_request_seconds = time.perf_counter() - request_started
        repair_score_delta = (
            second_validation_score - original_validation.overall_score
            if second_validation_score is not None
            else None
        )
        estimated_total_tokens = (
            estimated_input_tokens
            + initial_output_tokens
            + repair_input_tokens
            + repair_output_tokens
        )

        if prompt_debug:
            logger.info(
                "AI request diagnostics question=%r logical_gemini_calls=%d prompt_characters=%d "
                "prompt_words=%d estimated_input_tokens=%d initial_output_chars=%d "
                "initial_output_words=%d estimated_initial_output_tokens=%d initial_validation_passed=%s "
                "initial_validation_score=%.3f validation_passed=%s "
                "validation_score=%.3f repair_triggered=%s repair_prompt_characters=%d "
                "repair_prompt_words=%d estimated_repair_input_tokens=%d repair_output_chars=%d "
                "repair_output_words=%d estimated_repair_output_tokens=%d final_output_chars=%d "
                "final_output_words=%d estimated_final_output_tokens=%d estimated_total_tokens=%d finish_reason=%s "
                "response_generation_ms=%.2f validation_ms=%.2f repair_ms=%.2f total_request_ms=%.2f",
                request.question[:120],
                logical_gemini_calls,
                prompt_characters,
                prompt_words,
                estimated_input_tokens,
                initial_answer_chars,
                initial_answer_words,
                initial_output_tokens,
                original_validation.passed,
                original_validation.overall_score,
                validation.passed,
                validation.overall_score,
                retry_triggered,
                repair_prompt_characters,
                repair_prompt_words,
                repair_input_tokens,
                repaired_answer_chars,
                repaired_answer_words,
                repair_output_tokens,
                final_answer_chars,
                final_answer_words,
                final_output_tokens,
                estimated_total_tokens,
                "unavailable_provider_returns_text_only",
                response_generation_seconds * 1000,
                validation_seconds * 1000,
                repair_seconds * 1000,
                total_request_seconds * 1000,
            )
            logging.getLogger(__name__).info(
                "Response validation: passed=%s score=%.3f missing_sections=%s "
                "missing_evidence=%s generic_reasoning=%s word_count=%d "
                "hallucination_risk=%.3f validation_ms=%.2f",
                validation.passed,
                validation.overall_score,
                validation.missing_sections,
                validation.missing_repository_evidence,
                validation.generic_reasoning,
                validation.word_count,
                validation.hallucination_risk,
                validation_seconds * 1000,
            )
            logging.getLogger(__name__).info(
                "Response repair: original_validation_score=%.3f repair_reasons=%s "
                "retry_triggered=%s second_validation_score=%s score_improvement=%s "
                "repair_prompt_characters=%d repair_prompt_words=%d repair_output_estimated_tokens=%d",
                original_validation.overall_score,
                list(dict.fromkeys(repair_reasons)),
                retry_triggered,
                f"{second_validation_score:.3f}" if second_validation_score is not None else "not run",
                f"{repair_score_delta:+.3f}" if repair_score_delta is not None else "not run",
                repair_prompt_characters,
                repair_prompt_words,
                repair_output_tokens,
            )
            logger.info(
                "Validation evidence usage question=%r synthesized_areas=%s evidence_match_count=%d",
                request.question[:120],
                validation.synthesized_areas,
                len(validation.evidence_matches),
            )

        sources = self._collect_sources(request.analysis)

        return ChatResponse(
            answer=answer,
            sources=sources,
            validation=validation,
        )

    def _fallback_answer(self, question: str, error: str) -> str:
        normalized_error = error.lower()
        if "not configured" in normalized_error or "missing_api_key" in normalized_error:
            return (
                "## Configuration Error\n"
                "Gemini is not configured, so Atlas cannot produce a live repository answer right now.\n\n"
                "## Short Answer\n"
                "The assistant cannot generate a grounded response until the Gemini provider is configured.\n\n"
                "## Detailed Explanation\n"
                "Atlas has the repository analysis available locally, but it cannot call the LLM provider without a valid API key.\n\n"
                "## Recommendations\n"
                "- Configure GEMINI_API_KEY and MODEL_NAME in the backend environment.\n"
                "- Restart the backend and retry your question."
            )
        if "invalid_api_key" in normalized_error or "api key was rejected" in normalized_error:
            return (
                "## Provider Authentication Error\n"
                "Gemini rejected the configured API key. Check the key in the deployment secret settings.\n\n"
                "## Short Answer\n"
                "Atlas could not obtain a response because Gemini rejected its API key.\n\n"
                "## Detailed Explanation\n"
                "The provider returned an authentication failure. The repository question and analysis were not changed."
            )
        if "rate_limited" in normalized_error or "quota or rate limit" in normalized_error:
            return (
                "## Provider Rate Limit\n"
                "The Gemini API quota or rate limit has been exceeded. Please retry after the quota window resets."
            )
        if "timeout" in normalized_error or "did not respond in time" in normalized_error:
            return "## Provider Timeout\nThe AI provider did not respond in time. Please try again in a few moments."
        if "temporary_service_unavailable" in normalized_error or "temporarily experiencing high demand" in normalized_error or "temporarily unavailable" in normalized_error:
            return "## Provider Temporarily Unavailable\nThe Gemini service is temporarily experiencing high demand. Please try again in a few moments."
        if "model_unavailable" in normalized_error or "model or endpoint was not found" in normalized_error:
            return "## Model Unavailable\nThe configured Gemini model or endpoint was not found. Check MODEL_NAME in the deployment settings."
        if "network_failure" in normalized_error or "network failure" in normalized_error:
            return "## Network Error\nA network failure prevented contacting the Gemini service. Please try again shortly."
        if "invalid_request" in normalized_error:
            return "## Provider Request Error\nGemini rejected the generated request as invalid."
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
