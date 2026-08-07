import json
from typing import Any

from services.analyzers.detection_rules import (
    FRONTEND_RULES,
    NODE_BACKEND_RULES,
    PYTHON_BACKEND_RULES,
    JAVA_BACKEND_RULES,
    RUST_BACKEND_RULES,
    GO_BACKEND_RULES,
    DATABASE_RULES,
    CLOUD_FILES,
    CLOUD_KEYWORDS,
    CI_FILES,
    CONTAINER_FILES,
    PACKAGE_MANAGER_FILES,
    MOBILE_RULES,
    MOBILE_FILES,
    LANGUAGE_FILES,
)


class TechStackAnalyzer:
    """
    Detects repository technologies using:

    - repository tree
    - dependency manifests
    - configuration files

    No GitHub API calls occur here.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        files: dict[str, str],
    ) -> dict:

        paths = {item["path"] for item in tree}
        lower_paths = {path.lower() for path in paths}

        def find_files(filename: str) -> list[tuple[str, str]]:
            normalized = filename.lower()
            matches = []
            for path, content in files.items():
                path_lower = path.lower()
                if path_lower == normalized or path_lower.endswith("/" + normalized):
                    matches.append((path, content))
            return matches

        result = {
            "languages": [],
            "frontend": [],
            "backend": [],
            "database": [],
            "cloud": [],
            "ci_cd": [],
            "package_managers": [],
            "mobile": [],
            "containers": [],
            "technologies": [],
        }

        def add(category: str, value: str):
            if value not in result[category]:
                result[category].append(value)

        def add_technology(name: str, category: str, confidence: float, evidence: list[str]):
            technology = {
                "name": name,
                "category": category,
                "confidence": round(min(max(confidence, 0.0), 1.0), 2),
                "evidence": list(dict.fromkeys(evidence)),
            }
            if not any(
                item["name"] == technology["name"] and item["category"] == technology["category"]
                for item in result["technologies"]
            ):
                result["technologies"].append(technology)

        package_dependencies: dict[str, str] = {}
        for path, content in find_files("package.json"):
            try:
                package = json.loads(content) if content else {}
            except Exception:
                package = {}
            for dependency_name in package.get("dependencies", {}):
                package_dependencies[dependency_name] = package["dependencies"][dependency_name]
            for dependency_name in package.get("devDependencies", {}):
                package_dependencies[dependency_name] = package["devDependencies"][dependency_name]

        python_text_parts: list[str] = []
        java_text_parts: list[str] = []
        cargo_text_parts: list[str] = []
        go_mod_parts: list[str] = []
        composer_parts: list[str] = []

        for path, content in files.items():
            path_lower = path.lower()
            if path_lower.endswith("/requirements.txt") or path_lower == "requirements.txt":
                python_text_parts.append(content.lower())
            if path_lower.endswith("/pyproject.toml") or path_lower == "pyproject.toml":
                python_text_parts.append(content.lower())
            if path_lower.endswith("/pom.xml") or path_lower == "pom.xml":
                java_text_parts.append(content.lower())
            if path_lower.endswith("/build.gradle") or path_lower == "build.gradle":
                java_text_parts.append(content.lower())
            if path_lower.endswith("/build.gradle.kts") or path_lower == "build.gradle.kts":
                java_text_parts.append(content.lower())
            if path_lower.endswith("/cargo.toml") or path_lower == "cargo.toml":
                cargo_text_parts.append(content.lower())
            if path_lower.endswith("/go.mod") or path_lower == "go.mod":
                go_mod_parts.append(content.lower())
            if path_lower.endswith("/composer.json") or path_lower == "composer.json":
                composer_parts.append(content.lower())

        python_text = "\n".join(python_text_parts).lower()
        java_text = "\n".join(java_text_parts).lower()
        cargo_text = "\n".join(cargo_text_parts).lower()
        go_mod_text = "\n".join(go_mod_parts).lower()
        composer_text = "\n".join(composer_parts).lower()
        repository_text = "\n".join(
            [
                python_text,
                java_text,
                cargo_text,
                go_mod_text,
                composer_text,
                "\n".join(package_dependencies.keys()).lower(),
            ]
        )

        for path in lower_paths:
            for extension, language in LANGUAGE_FILES.items():
                if path.endswith(extension):
                    add("languages", language)
                    add_technology(language, "language", 0.9, [path])

        language_map = {
            "package.json": "JavaScript",
            "tsconfig.json": "TypeScript",
            "requirements.txt": "Python",
            "pyproject.toml": "Python",
            "pom.xml": "Java",
            "build.gradle": "Java",
            "build.gradle.kts": "Java",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "composer.json": "PHP",
        }

        for filename, language in language_map.items():
            if filename.lower() in lower_paths:
                add("languages", language)
                add_technology(language, "language", 0.95, [filename])

        for filename, manager in PACKAGE_MANAGER_FILES.items():
            if filename.lower() in lower_paths:
                add("package_managers", manager)
                add_technology(manager, "package_manager", 0.92, [filename])

        for dependency, framework in FRONTEND_RULES.items():
            if dependency in package_dependencies:
                add("frontend", framework)
                add_technology(framework, "frontend", 0.93, [dependency])

        if (
            "React" in result["frontend"]
            and (
                "vite.config.ts" in lower_paths
                or "vite.config.js" in lower_paths
            )
            and "Vite" not in result["frontend"]
        ):
            add("frontend", "Vite")
            add_technology("Vite", "frontend", 0.88, ["vite.config"])

        for dependency, framework in NODE_BACKEND_RULES.items():
            if dependency in package_dependencies:
                add("backend", framework)
                add_technology(framework, "backend", 0.93, [dependency])

        for keyword, framework in PYTHON_BACKEND_RULES.items():
            if keyword in python_text:
                add("backend", framework)
                add_technology(framework, "backend", 0.9, [keyword])

        for keyword, framework in JAVA_BACKEND_RULES.items():
            if keyword in java_text:
                add("backend", framework)
                add_technology(framework, "backend", 0.9, [keyword])

        for keyword, framework in RUST_BACKEND_RULES.items():
            if keyword in cargo_text:
                add("backend", framework)
                add_technology(framework, "backend", 0.9, [keyword])

        for keyword, framework in GO_BACKEND_RULES.items():
            if keyword in go_mod_text:
                add("backend", framework)
                add_technology(framework, "backend", 0.9, [keyword])

        for keyword, database in DATABASE_RULES.items():
            if keyword.lower() in repository_text:
                add("database", database)
                add_technology(database, "database", 0.86, [keyword])

        for filename, provider in CLOUD_FILES.items():
            if filename.lower() in lower_paths:
                add("cloud", provider)
                add_technology(provider, "cloud", 0.9, [filename])

        for keyword, provider in CLOUD_KEYWORDS.items():
            if keyword.lower() in repository_text:
                add("cloud", provider)
                add_technology(provider, "cloud", 0.84, [keyword])

        for indicator, provider in CI_FILES.items():
            indicator = indicator.lower()
            if any(path.startswith(indicator) or path == indicator for path in lower_paths):
                add("ci_cd", provider)
                add_technology(provider, "ci_cd", 0.9, [indicator])

        for indicator, container in CONTAINER_FILES.items():
            indicator = indicator.lower()
            if any(indicator in path for path in lower_paths):
                add("containers", container)
                add_technology(container, "container", 0.9, [indicator])

        for dependency, framework in MOBILE_RULES.items():
            if dependency in package_dependencies:
                add("mobile", framework)
                add_technology(framework, "mobile", 0.9, [dependency])

        for filename, platform in MOBILE_FILES.items():
            filename = filename.lower()
            if any(path.endswith(filename) for path in lower_paths):
                add("mobile", platform)
                add_technology(platform, "mobile", 0.88, [filename])

        for key in result:
            if key != "technologies":
                result[key] = sorted(set(result[key]))

        result["technologies"] = sorted(
            result["technologies"],
            key=lambda item: (item["category"], item["name"].lower()),
        )
        return result

    