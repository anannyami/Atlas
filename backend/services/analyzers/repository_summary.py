from __future__ import annotations

from typing import Any


class RepositorySummaryAnalyzer:
    """
    Generates a concise repository summary using repository metadata,
    README text, and the canonical tech stack.
    """

    def analyze(
        self,
        metadata: dict[str, Any],
        readme: str | None,
        tech_stack: dict,
        architecture: dict,
        classification: dict,
        structure: dict,
        health: dict,
        activity: dict,
    ) -> dict:
        repository_name = metadata.get("name", "This repository")
        description = self._clean_sentence(metadata.get("description"))
        readme_summary = self._extract_readme_summary(readme)
        topics = metadata.get("topics", []) or []
        languages = list(tech_stack.get("languages", []) or [])
        technology_names = [
            item.get("name", "")
            for item in (tech_stack.get("technologies", []) or [])
            if isinstance(item, dict) and item.get("name")
        ]

        primary_classification = classification.get("primary_classification") or classification.get("project_type") or "software project"
        architecture_style = architecture.get("style", "standard repository")
        architecture_summary = architecture.get("summary", "")

        overview_parts = []
        if description:
            overview_parts.append(description)
        elif readme_summary:
            overview_parts.append(readme_summary)
        elif topics:
            overview_parts.append(f"{repository_name} appears to focus on {', '.join(topics[:3])}.")
        else:
            overview_parts.append(f"{repository_name} appears to be a {primary_classification.lower()}.")

        if architecture_summary:
            overview_parts.append(architecture_summary)
        elif architecture_style:
            overview_parts.append(f"The repository follows a {architecture_style.lower()} architecture.")

        if languages:
            overview_parts.append(f"Primary languages are {', '.join(languages)}.")
        if technology_names:
            overview_parts.append(f"Detected technologies include {', '.join(technology_names)}.")

        overview_parts.append(
            f"Repository health is {health.get('overall_status', 'unknown').lower()} and activity is {activity.get('activity_level', 'unknown').lower()}."
        )

        purpose = self._build_purpose(
            primary_classification=primary_classification,
            architecture_style=architecture_style,
            metadata=metadata,
            readme_summary=readme_summary,
            topics=topics,
            languages=languages,
        )

        current_status = (
            f"{activity.get('activity_level', 'Unknown')} activity • "
            f"{activity.get('repository_maturity', 'Unknown')} repository • "
            f"Health Score {health.get('score', 0)}/100"
        )

        highlights = []
        if primary_classification:
            highlights.append(f"Classification: {primary_classification}")
        if architecture_style:
            highlights.append(f"Architecture: {architecture_style}")
        if languages:
            highlights.append(f"Languages: {', '.join(languages)}")
        if technology_names:
            highlights.append(f"Technologies: {', '.join(technology_names)}")
        if topics:
            highlights.append(f"Topics: {', '.join(topics[:5])}")
        highlights.append(f"Health: {health.get('score', 0)}/100")
        highlights.append(f"Activity: {activity.get('activity_level', 'Unknown')}")

        source_factors = []
        if description:
            source_factors.append("description")
        if readme_summary:
            source_factors.append("README")
        if topics:
            source_factors.append("topics")
        if languages:
            source_factors.append("languages")
        if architecture_style:
            source_factors.append("architecture")
        if technology_names:
            source_factors.append("tech stack")

        return {
            "overview": " ".join(part.strip() for part in overview_parts if part.strip()),
            "purpose": purpose,
            "current_status": current_status,
            "highlights": self._dedupe(highlights),
            "source_factors": self._dedupe(source_factors),
        }

    def _build_purpose(
        self,
        *,
        primary_classification: str,
        architecture_style: str,
        metadata: dict[str, Any],
        readme_summary: str,
        topics: list[str],
        languages: list[str],
    ) -> str:
        description = self._clean_sentence(metadata.get("description"))
        if description:
            return description
        if readme_summary:
            return readme_summary
        if topics:
            return f"This repository appears to be a {primary_classification.lower()} focused on {', '.join(topics[:3])}."
        if languages:
            return f"This repository appears to be a {primary_classification.lower()} implemented primarily with {', '.join(languages[:3])}."
        return f"This repository appears to be a {primary_classification.lower()} built using a {architecture_style.lower()} structure."

    def _extract_readme_summary(self, readme: str | None) -> str:
        if not readme:
            return ""
        lines = [line.strip() for line in readme.splitlines() if line.strip()]
        for line in lines:
            if line.startswith("#"):
                continue
            if len(line) >= 40:
                return self._clean_sentence(line)
        if lines:
            return self._clean_sentence(lines[0])
        return ""

    def _clean_sentence(self, text: str | None) -> str:
        if not text:
            return ""
        cleaned = text.strip()
        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."
        return cleaned

    def _dedupe(self, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
