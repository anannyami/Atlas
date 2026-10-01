from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from models.response_validation import ResponseValidationResult


class RepairPromptBuilder:
    """Build a one-shot repair instruction from validation findings and evidence."""

    ANALYSIS_KEYS = (
        "repository",
        "summary",
        "purpose",
        "repository_identity",
        "product_identity",
        "classification",
        "architecture",
        "tech_stack",
        "structure",
        "health",
        "activity",
        "blueprint",
        "knowledge",
    )

    def build(
        self,
        original_response: str,
        validation_result: ResponseValidationResult,
        question: str,
        repository_analysis: Mapping[str, Any],
    ) -> str:
        reasons = self._repair_reasons(validation_result)
        analysis_excerpt = self._analysis_excerpt(repository_analysis)

        return f"""You are repairing a repository-specific engineering answer after a quality check.

Return only the complete corrected answer. Preserve accurate content from the original answer, fix each listed issue, and follow the required six-section response structure. Do not mention this repair process or the validation score.

Original user question:
{question}

Original Gemini response:
{original_response}

Validation findings to address:
{chr(10).join(f'- {reason}' for reason in reasons) if reasons else '- Improve specificity and evidence coverage while preserving supported claims.'}

Repository analysis evidence (the only source of repository facts):
{analysis_excerpt}

Repair rules:
- Use repository facts only when supported by the analysis evidence above.
- Do not invent files, technologies, behaviors, metrics, design decisions, or security controls.
- If evidence is missing, explicitly state that it cannot be determined from the supplied analysis.
- Include these headings: Short Answer, Repository Overview, Detailed Explanation, Repository Evidence, Engineering Observations, Conclusion.
- Cite concrete analysis evidence in the Repository Evidence section.
- Add engineering reasoning and relevant cross-area synthesis without repeating unrelated material.
- If this is a follow-up, continue the established question and avoid repeating earlier explanations.
- Follow the requested answer length unless the user asked for brevity or the available repository evidence is genuinely limited.
"""

    def _repair_reasons(self, result: ResponseValidationResult) -> list[str]:
        reasons = list(result.issues)
        if result.missing_sections:
            reasons.append("Missing required headings: " + ", ".join(result.missing_sections))
        if result.missing_repository_evidence:
            reasons.append("Repository evidence gaps: " + "; ".join(result.missing_repository_evidence))
        if result.missing_engineering_observations:
            reasons.append("Engineering analysis gaps: " + "; ".join(result.missing_engineering_observations))
        if result.generic_reasoning:
            reasons.append("Replace generic filler with repository-specific, evidence-backed reasoning.")
        if result.hallucination_risk > 0:
            reasons.append(
                f"Hallucination risk is {result.hallucination_risk:.2f}; remove or qualify claims not supported by the analysis."
            )
        if result.followup_continuity < 0.5:
            reasons.append("Weak follow-up continuity: connect the answer to the current topic/component without repeating prior explanations.")
        return list(dict.fromkeys(reason for reason in reasons if reason.strip()))

    def _analysis_excerpt(self, analysis: Mapping[str, Any]) -> str:
        excerpt: dict[str, Any] = {}
        for key in self.ANALYSIS_KEYS:
            value = analysis.get(key)
            if value is None:
                continue
            if key == "knowledge" and isinstance(value, Mapping):
                value = {
                    field: value.get(field)
                    for field in ("readme", "evidence", "capabilities", "dependencies", "major_folders")
                    if value.get(field) is not None
                }
                if isinstance(value.get("readme"), str):
                    value["readme"] = value["readme"][:2000]
                if isinstance(value.get("evidence"), Sequence):
                    value["evidence"] = value["evidence"][:20]
            excerpt[key] = self._bounded(value)

        tree = analysis.get("repository_tree")
        if tree is None and isinstance(analysis.get("knowledge"), Mapping):
            tree = analysis["knowledge"].get("tree")
        if tree:
            excerpt["repository_tree_paths"] = self._tree_paths(tree)

        serialized = json.dumps(excerpt, ensure_ascii=False, default=self._model_dump)
        if len(serialized) > 12000:
            serialized = serialized[:11997].rstrip() + "..."
        return serialized

    def _bounded(self, value: Any, depth: int = 0) -> Any:
        if depth > 5:
            return "[nested detail omitted]"
        if isinstance(value, Mapping):
            return {
                str(key): self._bounded(item, depth + 1)
                for key, item in list(value.items())[:40]
            }
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [self._bounded(item, depth + 1) for item in value[:40]]
        if isinstance(value, str) and len(value) > 1500:
            return value[:1497].rstrip() + "..."
        if hasattr(value, "model_dump"):
            return self._bounded(value.model_dump(), depth + 1)
        return value

    def _tree_paths(self, tree: Any) -> list[str]:
        paths: list[str] = []

        def visit(nodes: Any) -> None:
            if not isinstance(nodes, Sequence) or isinstance(nodes, (str, bytes)):
                return
            for node in nodes:
                if len(paths) >= 80:
                    return
                if not isinstance(node, Mapping):
                    continue
                path = node.get("path")
                if path:
                    paths.append(str(path))
                visit(node.get("children") or [])

        visit(tree)
        return paths

    def _model_dump(self, value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return str(value)
