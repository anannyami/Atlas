from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    REPOSITORY_OVERVIEW = "repository_overview"
    ARCHITECTURE = "architecture"
    TECHNOLOGY = "technology"
    FOLDER_STRUCTURE = "folder_structure"
    REPOSITORY_TREE = "repository_tree"
    SECURITY = "security"
    PERFORMANCE = "performance"
    HEALTH = "health"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    DEVOPS = "devops"
    SCALABILITY = "scalability"
    COMPARISON = "comparison"
    IMPROVEMENT_SUGGESTIONS = "improvement_suggestions"
    CODE_EXPLANATION = "code_explanation"
    FOLLOW_UP = "follow_up"
    GENERAL_REPOSITORY_QUESTION = "general_repository_question"


class IntentEvidence(BaseModel):
    intent: Intent
    signal: str


class IntentClassification(BaseModel):
    intents: list[Intent] = Field(default_factory=list)
    contextual_intents: list[Intent] = Field(default_factory=list)
    is_follow_up: bool = False
    evidence: list[IntentEvidence] = Field(default_factory=list)


class IntentClassifier:
    """Classify repository questions with composable rules and recent dialogue."""

    _RULES: tuple[tuple[Intent, tuple[str, ...]], ...] = (
        (Intent.REPOSITORY_OVERVIEW, (
            r"\b(overview|summari[sz]e|summary|purpose|what is this (?:repo|repository|project)|what does (?:this|the) (?:repo|repository|project) do|who is this for|explain (?:this |the )?(?:repo|repository|project))\b",
        )),
        (Intent.ARCHITECTURE, (
            r"\b(architecture|architectural|system design|design pattern|components?|modules?|services?|request flow|data flow)\b",
        )),
        (Intent.TECHNOLOGY, (
            r"\b(technolog(?:y|ies)|tech stack|frameworks?|programming languages?|database|dependencies|libraries|why (?:was|is) [\w.+#-]+ chosen|(?:fastapi|django|flask|spring boot|react|vue|angular|express|nestjs|postgresql|mysql|mongodb|redis))\b",
        )),
        (Intent.FOLDER_STRUCTURE, (
            r"\b(folder structure|directory structure|repository structure|project structure|structure|project layout|folder|directory|entry point|important files)\b",
        )),
        (Intent.REPOSITORY_TREE, (
            r"\b(repository tree|file tree|directory tree|show the tree|list (?:the )?files)\b",
        )),
        (Intent.SECURITY, (
            r"\b(secur(?:ity|e)|vulnerabilit(?:y|ies)|authentication|authorization|permissions?|secrets?|encryption|threat model)\b",
        )),
        (Intent.PERFORMANCE, (
            r"\b(performance|latency|throughput|slow|fast|memory usage|optimi[sz]e|bottleneck)\b",
        )),
        (Intent.HEALTH, (
            r"\b(health|quality|maintain(?:ability|able)|maintenance|maturity|activity|test coverage|engineering practices)\b",
        )),
        (Intent.DOCUMENTATION, (
            r"\b(documentation|readme|docs?|installation guide|usage guide|getting started)\b",
        )),
        (Intent.DEPLOYMENT, (
            r"\b(deploy(?:ment)?|hosting|production environment|release process|run this in production)\b",
        )),
        (Intent.DEVOPS, (
            r"\b(devops|ci\s*/\s*cd|continuous integration|continuous deployment|pipeline|build automation|infrastructure as code)\b",
        )),
        (Intent.SCALABILITY, (
            r"\b(scal(?:e|es|ed|ing|ability)|scalable|capacity|handle more (?:users|traffic|requests))\b",
        )),
        (Intent.COMPARISON, (
            r"\b(compare|comparison|contrast|versus|vs\.?|difference(?:s)?|which .{1,40} better|trade-?offs?)\b",
        )),
        (Intent.IMPROVEMENT_SUGGESTIONS, (
            r"\b(improv(?:e|ement|ements)|recommend(?:ation|ations)?|suggest(?:ion|ions)?|what should (?:i|we) change|refactor|how could (?:this|the) (?:repository|repo|project) be improved)\b",
        )),
        (Intent.CODE_EXPLANATION, (
            r"\b(explain (?:the )?(?:code|function|class|method|implementation)|how does .{1,60} work|walk me through|trace (?:the )?(?:code|execution))\b",
        )),
    )

    _FOLLOW_UP_CUES = re.compile(
        r"\b(it|they|them)\b|\b(this|that|these|those)\b(?!\s+(?:repo|repository|project|architecture|structure|technology|technologies|tech stack|backend|frontend|api|service|module|folder|directory|framework))|\b(also|instead|what about|how about|and then|why is that|what about it)\b|^(and|but|so)\b",
        re.IGNORECASE,
    )

    def classify(
        self,
        question: str,
        recent_user_messages: list[str] | None = None,
    ) -> IntentClassification:
        question = question.strip()
        intents, evidence = self._classify_question(question)
        prior_user_messages = [
            message.strip()
            for message in (recent_user_messages or [])
            if message.strip() and message.strip() != question
        ]

        contextual_intents: list[Intent] = []
        for message in prior_user_messages[-3:]:
            prior_intents, _ = self._classify_question(message)
            for intent in prior_intents:
                if intent not in contextual_intents:
                    contextual_intents.append(intent)

        is_follow_up = bool(prior_user_messages) or bool(self._FOLLOW_UP_CUES.search(question))
        if is_follow_up:
            intents.append(Intent.FOLLOW_UP)
            evidence.append(IntentEvidence(
                intent=Intent.FOLLOW_UP,
                signal="recent conversation" if prior_user_messages else "context-dependent wording",
            ))

        if not intents:
            intents.append(Intent.GENERAL_REPOSITORY_QUESTION)
            evidence.append(IntentEvidence(
                intent=Intent.GENERAL_REPOSITORY_QUESTION,
                signal="no more specific intent matched",
            ))

        return IntentClassification(
            intents=intents,
            contextual_intents=contextual_intents,
            is_follow_up=is_follow_up,
            evidence=evidence,
        )

    def _classify_question(self, question: str) -> tuple[list[Intent], list[IntentEvidence]]:
        intents: list[Intent] = []
        evidence: list[IntentEvidence] = []

        for intent, patterns in self._RULES:
            for pattern in patterns:
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    intents.append(intent)
                    evidence.append(IntentEvidence(intent=intent, signal=match.group(0)))
                    break

        return intents, evidence
