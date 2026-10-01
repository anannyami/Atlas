from __future__ import annotations

import re

from pydantic import BaseModel, Field

from services.intent_classifier import Intent, IntentClassification


class ConversationState(BaseModel):
    """Compact state about the active engineering discussion only."""

    current_topic: str | None = None
    current_component: str | None = None
    current_intents: list[Intent] = Field(default_factory=list)
    discussed_topics: list[str] = Field(default_factory=list)
    pending_topics: list[str] = Field(default_factory=list)
    mentioned_technologies: list[str] = Field(default_factory=list)
    mentioned_components: list[str] = Field(default_factory=list)
    current_user_goal: str | None = None
    last_user_question: str | None = None


class ConversationStateService:
    """Update a conversational state without reading repository knowledge."""

    _TOPIC_LABELS = {
        Intent.REPOSITORY_OVERVIEW: "Repository Overview",
        Intent.ARCHITECTURE: "Architecture",
        Intent.TECHNOLOGY: "Technology",
        Intent.FOLDER_STRUCTURE: "Folder Structure",
        Intent.REPOSITORY_TREE: "Repository Tree",
        Intent.SECURITY: "Security",
        Intent.PERFORMANCE: "Performance",
        Intent.HEALTH: "Health",
        Intent.DOCUMENTATION: "Documentation",
        Intent.DEPLOYMENT: "Deployment",
        Intent.DEVOPS: "DevOps",
        Intent.SCALABILITY: "Scalability",
        Intent.COMPARISON: "Comparison",
        Intent.IMPROVEMENT_SUGGESTIONS: "Improvement Suggestions",
        Intent.CODE_EXPLANATION: "Code Explanation",
        Intent.FOLLOW_UP: "Follow-up",
        Intent.GENERAL_REPOSITORY_QUESTION: "Repository Question",
    }

    _TECHNOLOGY_NAMES = (
        "TypeScript", "JavaScript", "Python", "Java", "C#", "Go", "Rust",
        "React", "Vue", "Angular", "Svelte", "Next.js", "Vite", "FastAPI",
        "Django", "Flask", "Express", "NestJS", "Spring Boot", "PostgreSQL",
        "MySQL", "SQLite", "MongoDB", "Redis", "Docker", "Kubernetes",
        "AWS", "Azure", "Google Cloud", "GitHub Actions", "Terraform",
    )

    _COMPONENT_NAMES = (
        ("backend", "Backend"),
        ("server-side", "Backend"),
        ("frontend", "Frontend"),
        ("client-side", "Frontend"),
        ("api", "API"),
        ("database", "Database"),
        ("authentication", "Authentication"),
        ("authorization", "Authorization"),
        ("deployment", "Deployment"),
        ("worker", "Worker"),
        ("service", "Service"),
        ("module", "Module"),
    )

    def update(
        self,
        state: ConversationState | None,
        question: str,
        classification: IntentClassification,
    ) -> ConversationState:
        previous = state or ConversationState()
        clean_question = question.strip()

        topical_intents = [
            intent
            for intent in classification.intents
            if intent not in {Intent.FOLLOW_UP, Intent.GENERAL_REPOSITORY_QUESTION}
        ]
        topic_labels = [self._TOPIC_LABELS[intent] for intent in topical_intents]
        primary_topic = topic_labels[0] if topic_labels else previous.current_topic

        mentioned_components = self._ordered_union(
            previous.mentioned_components,
            self._find_components(clean_question),
        )
        current_component = self._find_components(clean_question)
        subtopics = {"Authentication", "Authorization"}
        primary_components = [
            component
            for component in current_component
            if component not in subtopics
        ]
        resolved_component = (
            primary_components[0]
            if primary_components
            else previous.current_component
        )

        current_turn_technologies = self._find_technologies(clean_question)
        pending_topics = [
            topic
            for topic in previous.pending_topics
            if topic not in topic_labels
        ]

        return ConversationState(
            current_topic=primary_topic,
            current_component=resolved_component,
            current_intents=classification.intents,
            discussed_topics=self._ordered_union(previous.discussed_topics, topic_labels),
            pending_topics=pending_topics,
            mentioned_technologies=self._ordered_union(
                previous.mentioned_technologies,
                current_turn_technologies,
            ),
            mentioned_components=mentioned_components,
            current_user_goal=clean_question or previous.current_user_goal,
            last_user_question=clean_question or previous.last_user_question,
        )

    def _find_technologies(self, text: str) -> list[str]:
        found: list[tuple[int, str]] = []
        for technology in self._TECHNOLOGY_NAMES:
            match = re.search(rf"(?<!\w){re.escape(technology)}(?!\w)", text, re.IGNORECASE)
            if match:
                found.append((match.start(), technology))
        return [name for _, name in sorted(found)]

    def _find_components(self, text: str) -> list[str]:
        found: list[tuple[int, str]] = []
        for term, label in self._COMPONENT_NAMES:
            match = re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
            if match:
                found.append((match.start(), label))
        ordered: list[str] = []
        for _, label in sorted(found):
            if label not in ordered:
                ordered.append(label)
        return ordered

    def _ordered_union(self, existing: list[str], additions: list[str]) -> list[str]:
        return list(dict.fromkeys([*existing, *additions]))