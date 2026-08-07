from collections import defaultdict
from typing import Any


def _normalize_text(values: list[str]) -> str:
    return " ".join(values).lower()


class ProjectClassificationAnalyzer:
    """
    Determines what kind of software project a repository represents.

    Classification is score-based and consumes the canonical tech stack.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        tech_stack: dict,
        metadata: dict[str, Any] | None = None,
        readme: str | None = None,
    ) -> dict:

        paths = {item["path"] for item in tree}
        lower_paths = {path.lower() for path in paths}

        metadata = metadata or {}
        topic_text = _normalize_text(metadata.get("topics", []))

        frontend = [item.lower() for item in tech_stack.get("frontend", [])]
        backend = [item.lower() for item in tech_stack.get("backend", [])]
        containers = [item.lower() for item in tech_stack.get("containers", [])]
        cloud = [item.lower() for item in tech_stack.get("cloud", [])]
        ci_cd = [item.lower() for item in tech_stack.get("ci_cd", [])]
        languages = [item.lower() for item in tech_stack.get("languages", [])]
        technologies = [
            (item.get("name") or "").lower()
            for item in (tech_stack.get("technologies", []) or [])
            if isinstance(item, dict)
        ]

        scores: dict[str, float] = defaultdict(float)
        evidence_map: dict[str, list[str]] = defaultdict(list)

        def add_score(category: str, weight: float, evidence: list[str]):
            scores[category] += weight
            if evidence:
                evidence_map[category].extend(evidence)

        def has_path_prefix(*prefixes: str) -> bool:
            return any(path.startswith(prefixes) for path in lower_paths for prefix in prefixes)

        def has_path_suffix(*suffixes: str) -> bool:
            return any(path.endswith(suffixes) for path in lower_paths for suffix in suffixes)

        for framework in frontend:
            if "react" in framework:
                add_score("Web Application", 40, [framework])
            elif any(token in framework for token in ("vue", "angular", "svelte", "next")):
                add_score("Web Application", 40, [framework])
            elif "vite" in framework:
                add_score("Web Application", 20, [framework])
            elif "tailwind" in framework:
                add_score("Web Application", 10, [framework])

        for framework in backend:
            if "fastapi" in framework:
                add_score("REST API", 40, [framework])
            elif "spring" in framework:
                add_score("REST API", 40, [framework])
            elif any(token in framework for token in ("express", "nestjs", "fastify")):
                add_score("REST API", 35, [framework])
            elif any(token in framework for token in ("django", "flask")):
                add_score("REST API", 25, [framework])

        if has_path_prefix("src/", "app/", "pages/", "frontend/", "web/", "client/"):
            add_score("Web Application", 20, ["layout folders"])
        if has_path_suffix("app.tsx", "app.ts", "app.jsx", "app.js", "page.tsx", "page.ts"):
            add_score("Web Application", 20, ["app entrypoint"])
        if has_path_prefix("pages/", "routes/", "api/", "server/", "backend/"):
            add_score("REST API", 20, ["api layout"])

        for name in technologies:
            if name in {"terraform"}:
                add_score("Infrastructure", 60, [name])
            elif name in {"helm"}:
                add_score("Infrastructure", 50, [name])
            elif name in {"kubernetes"}:
                add_score("Infrastructure", 60, [name])
            elif name in {"vercel", "netlify", "aws", "azure", "firebase"}:
                add_score("Infrastructure", 8, [name])

        if cloud:
            for item in cloud:
                add_score("Infrastructure", 4, [item])

        if has_path_prefix("cli/", "cmd/", "bin/"):
            add_score("CLI", 30, ["cli layout"])
        if any(token in _normalize_text(languages + technologies + frontend + backend) for token in ("argparse", "click", "typer", "commander")):
            add_score("CLI", 10, ["cli tooling"])

        if any(token in technologies for token in ("flutter", "react native", "kotlin", "swift")):
            add_score("Mobile", 30, ["mobile stack"])
        if has_path_prefix("mobile/", "android/", "ios/", "flutter/"):
            add_score("Mobile", 20, ["mobile layout"])

        if any(token in technologies for token in ("pandas", "numpy", "tensorflow", "pytorch", "scikit-learn")):
            add_score("Data Science", 30, ["data science tooling"])
        if any(token in lower_paths for token in ("notebook", "notebooks", "dataset", "datasets")):
            add_score("Data Science", 10, ["data science layout"])

        if not scores:
            scores["Library"] = 0.5
            evidence_map["Library"] = ["fallback heuristic"]

        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0].lower()))
        primary_name, primary_score = ordered[0]
        secondary = ordered[1:4]

        return {
            "project_type": primary_name,
            "primary_classification": primary_name,
            "secondary_classifications": [
                {
                    "name": name,
                    "confidence": round(min(0.99, 0.55 + score / 200), 2),
                    "evidence": list(dict.fromkeys(evidence_map.get(name, []))),
                }
                for name, score in secondary
            ],
            "confidence": round(min(0.99, 0.55 + primary_score / 200), 2),
        }