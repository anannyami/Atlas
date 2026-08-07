from __future__ import annotations

from collections import defaultdict
from typing import Any


class ArchitectureAnalyzer:
    """
    Interprets the canonical tech stack and repository layout to infer
    architecture style and supporting signals.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        files: dict[str, str] | None = None,
        tech_stack: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        readme: str | None = None,
    ) -> dict:
        files = files or {}
        tech_stack = tech_stack or {}
        metadata = metadata or {}

        paths = {item["path"] for item in tree}
        lower_paths = {path.lower() for path in paths}

        result = {
            "style": "Standard Repository",
            "applications": [],
            "workspace": [],
            "modules": [],
            "deployment": [],
            "frontend_frameworks": [],
            "backend_frameworks": [],
            "databases": [],
            "cloud": [],
            "authentication": [],
            "api_styles": [],
            "architecture_patterns": [],
            "organization": [],
            "confidence": 0.0,
            "summary": "",
        }

        def add(category: str, value: str):
            if value not in result[category]:
                result[category].append(value)

        def add_signal(category: str, name: str, confidence: float, evidence: list[str]):
            add(
                category,
                {
                    "name": name,
                    "confidence": round(confidence, 2),
                    "evidence": evidence,
                },
            )

        def has_path_prefix(*prefixes: str) -> bool:
            return any(path.startswith(prefixes) for path in lower_paths for prefix in prefixes)

        for name in tech_stack.get("frontend", []) or []:
            add_signal("frontend_frameworks", name, 0.9, [name])
        for name in tech_stack.get("backend", []) or []:
            add_signal("backend_frameworks", name, 0.9, [name])
        for name in tech_stack.get("database", []) or []:
            add_signal("databases", name, 0.9, [name])
        for name in tech_stack.get("cloud", []) or []:
            add_signal("cloud", name, 0.9, [name])
        for name in tech_stack.get("containers", []) or []:
            add("deployment", name)
        for name in tech_stack.get("ci_cd", []) or []:
            add("deployment", name)

        if any(path.startswith(("web/", "frontend/", "client/", "ui/")) for path in lower_paths):
            add("applications", "Web")
        if any(path.startswith(("mobile/", "android/", "ios/", "flutter/")) for path in lower_paths):
            add("applications", "Mobile")
        if any(path.startswith(("desktop/", "electron/", "tauri/")) for path in lower_paths):
            add("applications", "Desktop")
        if any(path.startswith(("cli/", "cmd/", "bin/")) for path in lower_paths):
            add("applications", "CLI")

        if any(path.startswith(("apps/", "packages/", "modules/")) for path in lower_paths):
            add("workspace", "Monorepo")
            add("modules", "Workspace Modules")
        if any(path.startswith(("services/", "service/")) for path in lower_paths):
            add("organization", "Service layer")
        if any(path.startswith(("models/", "model/", "domain/", "entities/")) for path in lower_paths):
            add("organization", "Model layer")
        if any(path.startswith(("controllers/", "controller/", "routes/", "handlers/")) for path in lower_paths):
            add("organization", "Controller layer")

        api_evidence = []
        if any(path.startswith(("api/", "backend/api/", "routes/")) for path in lower_paths):
            api_evidence.append("api layout")
        if tech_stack.get("backend"):
            api_evidence.append("backend stack")
        if api_evidence:
            add_signal("api_styles", "REST", 0.8, api_evidence)

        layer_dirs = {
            "Presentation": ("frontend/", "client/", "web/", "ui/", "components/", "pages/", "views/"),
            "Backend": ("backend/", "api/", "server/"),
            "Service": ("services/", "service/"),
            "Persistence": ("models/", "model/", "repositories/", "database/", "db/", "entities/", "domain/"),
        }
        layers_present = []
        for layer_name, prefixes in layer_dirs.items():
            if any(path.startswith(prefixes) for path in lower_paths for prefix in prefixes):
                layers_present.append(layer_name)
                add("organization", layer_name)

        if layers_present:
            add_signal("architecture_patterns", "Layered Architecture", min(0.96, 0.72 + len(layers_present) * 0.05), layers_present)

        style_scores = defaultdict(lambda: {"score": 0.0, "evidence": []})

        def raise_style(name: str, score: float, evidence: list[str]):
            current = style_scores[name]
            if score > current["score"]:
                current["score"] = score
            for item in evidence:
                if item not in current["evidence"]:
                    current["evidence"].append(item)

        if tech_stack.get("frontend") and tech_stack.get("backend"):
            raise_style("Client-Server", 0.95, ["frontend/backend split"])
        if any(path.startswith(("apps/", "packages/", "modules/")) for path in lower_paths):
            raise_style("Monorepo", 0.9, ["workspace folders"])
        if layers_present:
            raise_style("Layered Architecture", min(0.96, 0.7 + len(layers_present) * 0.05), layers_present)
        if not style_scores:
            raise_style("Monolith", 0.6, ["single application layout"])

        chosen_style = sorted(style_scores.items(), key=lambda item: (-item[1]["score"], item[0].lower()))[0]
        result["style"] = chosen_style[0]
        result["confidence"] = round(chosen_style[1]["score"], 2)

        result["summary"] = " ".join(
            part
            for part in [
                f"The repository most closely matches a {result['style'].lower()} architecture.",
                f"Detected framework signals include {', '.join(item['name'] for item in result['frontend_frameworks'][:2] + result['backend_frameworks'][:2])}." if (result["frontend_frameworks"] or result["backend_frameworks"]) else "",
                f"Deployment uses {', '.join(result['deployment'][:3])}." if result["deployment"] else "",
            ]
            if part
        )

        for key in ("applications", "workspace", "modules", "deployment", "organization"):
            result[key] = sorted(dict.fromkeys(result[key]), key=str.lower)

        return result
