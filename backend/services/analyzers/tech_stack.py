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

        paths = {
            item["path"]
            for item in tree
        }

        lower_paths = {
            p.lower()
            for p in paths
        }

        def get_file(filename: str) -> str:
            """
            Return the contents of the first matching file,
            regardless of directory.
            """

            for path, content in files.items():
                if (
                    path == filename
                    or path.endswith("/" + filename)
                ):
                    return content

            return ""

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
        }

        # ----------------------------------------------------
        # Helper
        # ----------------------------------------------------

        def add(category: str, value: str):

            if value not in result[category]:
                result[category].append(value)

        # ----------------------------------------------------
        # Load important files
        # ----------------------------------------------------

        package_json = get_file("package.json")

        package = {}

        if package_json:

            try:
                package = json.loads(package_json)

            except Exception:
                package = {}

        dependencies = {}

        dependencies.update(
            package.get("dependencies", {})
        )

        dependencies.update(
            package.get("devDependencies", {})
        )

        requirements = get_file(
            "requirements.txt"
        ).lower()

        pyproject = get_file(
            "pyproject.toml"
        ).lower()

        python_text = (
            requirements
            + "\n"
            + pyproject
        )

        pom = get_file(
            "pom.xml"
        ).lower()

        gradle = (
            get_file("build.gradle")
            + "\n"
            + get_file("build.gradle.kts")
        ).lower()

        java_text = pom + gradle

        cargo = get_file(
            "Cargo.toml"
        ).lower()

        go_mod = get_file(
            "go.mod"
        ).lower()

        repository_text = "\n".join([
            python_text,
            java_text,
            cargo,
            go_mod,
            package_json.lower(),
        ])

        # ----------------------------------------------------
        # Languages
        # ----------------------------------------------------

        for path in lower_paths:

            for extension, language in LANGUAGE_FILES.items():

                if path.endswith(extension):
                    add("languages", language)

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

        # ----------------------------------------------------
        # Package Managers
        # ----------------------------------------------------

        for filename, manager in PACKAGE_MANAGER_FILES.items():

            if filename.lower() in lower_paths:
                add("package_managers", manager)

        # ----------------------------------------------------
        # Frontend
        # ----------------------------------------------------

        for dependency, framework in FRONTEND_RULES.items():

            if dependency in dependencies:
                add("frontend", framework)

        if (
            "React" in result["frontend"]
            and (
                "vite.config.ts" in lower_paths
                or "vite.config.js" in lower_paths
            )
            and "Vite" not in result["frontend"]
        ):
            add("frontend", "Vite")

        # ----------------------------------------------------
        # Node Backend
        # ----------------------------------------------------

        for dependency, framework in NODE_BACKEND_RULES.items():

            if dependency in dependencies:
                add("backend", framework)

        # ----------------------------------------------------
        # Python Backend
        # ----------------------------------------------------

        for keyword, framework in PYTHON_BACKEND_RULES.items():

            if keyword in python_text:
                add("backend", framework)

        # ----------------------------------------------------
        # Java Backend
        # ----------------------------------------------------

        for keyword, framework in JAVA_BACKEND_RULES.items():

            if keyword in java_text:
                add("backend", framework)

        # ----------------------------------------------------
        # Rust Backend
        # ----------------------------------------------------

        for keyword, framework in RUST_BACKEND_RULES.items():

            if keyword in cargo:
                add("backend", framework)

        # ----------------------------------------------------
        # Go Backend
        # ----------------------------------------------------

        for keyword, framework in GO_BACKEND_RULES.items():

            if keyword in go_mod:
                add("backend", framework)

        # ----------------------------------------------------
        # Databases
        # ----------------------------------------------------

        for keyword, database in DATABASE_RULES.items():

            if keyword.lower() in repository_text:
                add("database", database)

                # ----------------------------------------------------
        # Cloud
        # ----------------------------------------------------

        for filename, provider in CLOUD_FILES.items():

            if filename.lower() in lower_paths:
                add("cloud", provider)

        for keyword, provider in CLOUD_KEYWORDS.items():

            if keyword.lower() in repository_text:
                add("cloud", provider)

        # ----------------------------------------------------
        # CI/CD
        # ----------------------------------------------------

        for indicator, provider in CI_FILES.items():

            indicator = indicator.lower()

            if any(
                path.startswith(indicator)
                or path == indicator
                for path in lower_paths
            ):
                add("ci_cd", provider)

        # ----------------------------------------------------
        # Containers
        # ----------------------------------------------------

        for indicator, container in CONTAINER_FILES.items():

            indicator = indicator.lower()

            if any(
                indicator in path
                for path in lower_paths
            ):
                add("containers", container)

        # ----------------------------------------------------
        # Mobile
        # ----------------------------------------------------

        for dependency, framework in MOBILE_RULES.items():

            if dependency in dependencies:
                add("mobile", framework)

        for filename, platform in MOBILE_FILES.items():

            filename = filename.lower()

            if any(
                path.endswith(filename)
                for path in lower_paths
            ):
                add("mobile", platform)

        # ----------------------------------------------------
        # Cleanup
        # ----------------------------------------------------

        for key in result:

            result[key] = sorted(
                set(result[key])
            )

        print("\n========== TECH STACK RESULT ==========")
        print(result)
        print("=======================================\n")

        return result

    