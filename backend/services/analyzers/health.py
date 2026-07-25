from typing import Any


class HealthAnalyzer:
    """
    Evaluates the overall health of a repository
    based on common engineering best practices.
    """

    def analyze(
        self,
        metadata: dict[str, Any],
        tree: list[dict[str, Any]],
        tech_stack: dict,
        releases: list[dict[str, Any]],
    ) -> dict:

        paths = {
            item["path"]
            for item in tree
        }

        checks = {
            "readme": False,
            "license": False,
            "docker": False,
            "ci_cd": False,
            "tests": False,
            "gitignore": False,
            "releases": False,
            "issues_enabled": False,
        }

        weights = {
            "readme": 20,
            "license": 10,
            "docker": 10,
            "ci_cd": 15,
            "tests": 20,
            "gitignore": 5,
            "releases": 10,
            "issues_enabled": 10,
        }

        #
        # README
        #

        if any(
            path.lower().startswith("readme")
            for path in paths
        ):
            checks["readme"] = True

        #
        # LICENSE
        #

        if any(
            path.upper().startswith("LICENSE")
            for path in paths
        ):
            checks["license"] = True

        #
        # Docker
        #

        checks["docker"] = "Docker" in tech_stack["containers"]

        #
        # CI/CD
        #

        checks["ci_cd"] = (
            len(
                tech_stack["ci_cd"]
            )
            > 0
        )

        #
        # Tests
        #

        test_dirs = (
            "tests",
            "test",
            "__tests__",
            "spec",
            "testing",
        )

        test_files = (
            "_test.py",
            ".test.ts",
            ".test.js",
            ".spec.ts",
            ".spec.js",
        )

        if any(
            path.startswith(test_dirs)
            or path.endswith(test_files)
            for path in paths
        ):
            checks["tests"] = True

        #
        # .gitignore
        #

        if ".gitignore" in paths:
            checks["gitignore"] = True

        #
        # GitHub metadata
        #

        checks["issues_enabled"] = metadata.get(
            "has_issues",
            False,
        )

        checks["releases"] = len(releases) > 0
        

        #
        # Score
        #

        earned = sum(
            weights[name]
            for name, passed in checks.items()
            if passed
        )

        total = sum(weights.values())

        score = round((earned / total) * 100)

        if score >= 90:
            health = "Excellent"
        elif score >= 75:
            health = "Good"
        elif score >= 60:
            health = "Fair"
        else:
            health = "Needs Improvement"

        return {
            "score": score,
            "health": health,
            "checks": checks,
        }