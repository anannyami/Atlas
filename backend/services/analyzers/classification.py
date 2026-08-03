from collections import Counter
from typing import Any


def _normalize_text(values: list[str]) -> str:
    return " ".join(values).lower()


class ProjectClassificationAnalyzer:
    """
    Determines what kind of software project
    a repository represents.

    Uses:
    - repository structure
    - detected technologies

    No GitHub API calls occur here.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        tech_stack: dict,
        metadata: dict[str, Any] | None = None,
        readme: str | None = None,
    ) -> dict:

        paths = {
            item["path"]
            for item in tree
        }

        metadata = metadata or {}
        readme_text = (readme or "").lower()
        topic_text = _normalize_text(metadata.get("topics", []))

        frontend = [item.lower() for item in tech_stack.get("frontend", [])]
        backend = [item.lower() for item in tech_stack.get("backend", [])]
        languages = [item.lower() for item in tech_stack.get("languages", [])]
        package_managers = [item.lower() for item in tech_stack.get("package_managers", [])]

        signals: list[tuple[str, float, list[str]]] = []

        def add_signal(name: str, confidence: float, evidence: list[str]):
            signals.append((name, confidence, evidence))

        tree_text = " ".join(sorted(paths)).lower()
        source_text = " ".join(
            [
                tree_text,
                readme_text,
                topic_text,
                _normalize_text(frontend),
                _normalize_text(backend),
                _normalize_text(languages),
                _normalize_text(package_managers),
            ]
        )

        def contains_any(*needles: str) -> bool:
            return any(needle in source_text for needle in needles)

        # Web Application
        web_evidence = []
        for keyword in ("react", "vue", "angular", "svelte", "next.js", "nuxt", "astro", "vite"):
            if keyword in source_text:
                web_evidence.append(keyword)
        if any(path.startswith(("web/", "frontend/", "client/", "ui/", "src/")) for path in paths) and web_evidence:
            add_signal("Web Application", 0.98, web_evidence)

        # REST API
        api_evidence = []
        for keyword in ("api", "rest", "fastapi", "express", "spring boot", "openapi", "swagger", "controller"):
            if keyword in source_text:
                api_evidence.append(keyword)
        if api_evidence:
            add_signal("REST API", min(0.97, 0.72 + len(api_evidence) * 0.05), api_evidence)

        # CLI
        cli_evidence = []
        for keyword in ("cli", "command line", "cmd/", "bin/", "argparse", "click", "typer"):
            if keyword in source_text:
                cli_evidence.append(keyword)
        if cli_evidence:
            add_signal("CLI", min(0.95, 0.7 + len(cli_evidence) * 0.05), cli_evidence)

        # Desktop
        desktop_evidence = []
        for keyword in ("electron", "tauri", "desktop", "wpf", "winforms"):
            if keyword in source_text:
                desktop_evidence.append(keyword)
        if desktop_evidence:
            add_signal("Desktop App", min(0.95, 0.72 + len(desktop_evidence) * 0.05), desktop_evidence)

        # Mobile
        mobile_evidence = []
        for keyword in ("android", "ios", "flutter", "react native", "kotlin", "swift"):
            if keyword in source_text:
                mobile_evidence.append(keyword)
        if mobile_evidence:
            if "flutter" in mobile_evidence:
                add_signal("Flutter", 0.96, mobile_evidence)
            if "android" in mobile_evidence:
                add_signal("Android", 0.92, mobile_evidence)
            if "ios" in mobile_evidence or "swift" in mobile_evidence:
                add_signal("iOS", 0.92, mobile_evidence)

        # Machine Learning / Data Science
        ml_evidence = []
        for keyword in ("notebook", "notebooks", "dataset", "datasets", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn"):
            if keyword in source_text:
                ml_evidence.append(keyword)
        if ml_evidence:
            add_signal("Machine Learning", min(0.95, 0.72 + len(ml_evidence) * 0.05), ml_evidence)
            if any(keyword in source_text for keyword in ("notebook", "notebooks", "dataset", "datasets", "pandas", "numpy")):
                add_signal("Data Science", min(0.93, 0.68 + len(ml_evidence) * 0.04), ml_evidence)

        # Infrastructure / DevOps / Automation
        infra_evidence = []
        for keyword in ("terraform", "ansible", "helm", "kubernetes", "docker", ".github/workflows", "ci", "cd", "script", "automation"):
            if keyword in source_text:
                infra_evidence.append(keyword)
        if infra_evidence:
            add_signal("Infrastructure", min(0.96, 0.7 + len(infra_evidence) * 0.05), infra_evidence)
            add_signal("DevOps Tool", min(0.94, 0.64 + len(infra_evidence) * 0.05), infra_evidence)
            if "automation" in source_text or "script" in source_text:
                add_signal("Automation Tool", min(0.92, 0.62 + len(infra_evidence) * 0.04), infra_evidence)

        # Library / SDK / Boilerplate / Template / Portfolio / Game / Browser Extension
        if any(path.startswith(("examples/", "example/")) for path in paths) and any(path.endswith(("setup.py", "pyproject.toml", "package.json", "Cargo.toml")) for path in paths):
            add_signal("Library", 0.9, ["examples", "package metadata"])
            add_signal("SDK", 0.78, ["package metadata"])

        if any(keyword in source_text for keyword in ("template", "boilerplate", "starter", "scaffold")):
            add_signal("Template", 0.93, ["template keywords"])
            add_signal("Boilerplate", 0.9, ["template keywords"])

        if any(keyword in source_text for keyword in ("portfolio", "personal website", "showcase")):
            add_signal("Portfolio", 0.9, ["portfolio keywords"])

        if any(keyword in source_text for keyword in ("game", "unity", "godot", "unreal")):
            add_signal("Game", 0.9, ["game keywords"])

        if any(keyword in source_text for keyword in ("browser extension", "chrome extension", "firefox extension", "manifest v3")):
            add_signal("Browser Extension", 0.96, ["extension keywords"])

        if not signals:
            signals.append(("Library", 0.5, ["fallback heuristic"]))

        ordered = sorted(signals, key=lambda item: (-item[1], item[0].lower()))
        primary_name, primary_confidence, primary_evidence = ordered[0]
        secondary = ordered[1:4]

        return {
            "project_type": primary_name,
            "primary_classification": primary_name,
            "secondary_classifications": [
                {
                    "name": name,
                    "confidence": confidence,
                    "evidence": evidence,
                }
                for name, confidence, evidence in secondary
            ],
            "confidence": round(primary_confidence, 2),
        }