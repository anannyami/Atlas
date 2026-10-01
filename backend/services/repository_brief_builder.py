from __future__ import annotations

from typing import Any


class RepositoryBriefBuilder:
    """Create a concise repository overview from AnalysisResponse data."""

    def build(self, analysis: dict[str, Any]) -> str:
        repository = self._mapping(analysis.get("repository"))
        summary = self._mapping(analysis.get("summary"))
        purpose = self._mapping(analysis.get("purpose"))
        architecture = self._mapping(analysis.get("architecture"))
        structure = self._mapping(analysis.get("structure"))
        tech_stack = self._mapping(analysis.get("tech_stack"))
        activity = self._mapping(analysis.get("activity"))
        classification = self._mapping(analysis.get("classification"))
        knowledge = self._mapping(analysis.get("knowledge"))

        repository_name = repository.get("full_name") or repository.get("name") or "Repository"
        overview = summary.get("overview") or "Unavailable in repository analysis."
        purpose_text = purpose.get("what") or purpose.get("why") or summary.get("purpose")
        architecture_summary = architecture.get("summary") or architecture.get("style")
        technology_overview = self._technology_overview(tech_stack)
        organization = structure.get("major_directories") or structure.get("major_modules") or []
        maturity = activity.get("repository_maturity")
        identity = self._mapping(analysis.get("repository_identity"))
        product = self._mapping(analysis.get("product_identity"))
        components = self._unique(
            [
                *self._strings(architecture.get("modules")),
                *self._strings(structure.get("major_modules")),
                *self._strings(structure.get("major_directories")),
                *self._strings(knowledge.get("major_folders")),
            ]
        )

        observations = self._unique(
            [
                *self._strings(summary.get("highlights")),
                *self._strings(activity.get("explanations")),
                *self._strings(analysis.get("repository_dna", {}).get("strengths")
                               if isinstance(analysis.get("repository_dna"), dict) else None),
            ]
        )

        engineering_style = self._first_text(
            analysis.get("repository_dna"), "engineering_style"
        ) or self._first_text(architecture, "style")

        lines = [
            f"Repository: {repository_name}",
            f"Repository Purpose: {self._first_text(purpose, 'what', 'why') or self._first_text(summary, 'purpose') or overview}",
            f"Architecture Summary: {self._text(architecture_summary)}",
            f"Technology Overview: {technology_overview}",
            f"Engineering Style: {self._text(engineering_style)}",
            f"Repository Organization: {self._join(organization)}",
            f"Engineering Maturity: {self._text(maturity)}",
            f"Important Components: {self._join(components)}",
            f"Key Engineering Observations: {self._join(observations)}",
        ]

        identity_summary = self._first_text(identity, "description", "tagline") or self._first_text(
            product, "summary", "title"
        )
        if identity_summary:
            lines.insert(1, f"Repository Identity: {identity_summary}")

        return "\n".join(lines)

    def _technology_overview(self, tech_stack: dict[str, Any]) -> str:
        categories = (
            ("Languages", "languages"),
            ("Frontend", "frontend"),
            ("Backend", "backend"),
            ("Data", "database"),
            ("Cloud", "cloud"),
            ("DevOps", "ci_cd"),
            ("Containers", "containers"),
        )
        entries = [
            f"{label}: {self._join(tech_stack.get(key))}"
            for label, key in categories
            if self._strings(tech_stack.get(key))
        ]
        return "; ".join(entries) or "Unavailable in repository analysis."

    def _mapping(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            result = value.model_dump()
            return result if isinstance(result, dict) else {}
        return {}

    def _first_text(self, value: Any, *keys: str) -> str | None:
        mapping = self._mapping(value)
        for key in keys:
            text = self._text(mapping.get(key))
            if text != "Unavailable in repository analysis.":
                return text
        return None

    def _text(self, value: Any) -> str:
        if value is None:
            return "Unavailable in repository analysis."
        text = str(value).strip()
        return text or "Unavailable in repository analysis."

    def _strings(self, value: Any) -> list[str]:
        if not isinstance(value, (list, tuple, set)):
            return []
        result = []
        for item in value:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    result.append(str(name))
            elif item:
                result.append(str(item))
        return result

    def _join(self, value: Any) -> str:
        items = self._strings(value)
        return ", ".join(items) if items else "Unavailable in repository analysis."

    def _unique(self, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value for value in values if value.strip()))