from typing import Any


class HealthAnalyzer:
    """
    Evaluates repository health using documentation, governance, automation,
    testing and community signals.
    """

    def analyze(
        self,
        metadata: dict[str, Any],
        tree: list[dict[str, Any]],
        tech_stack: dict,
        releases: list[dict[str, Any]],
        readme: str | None = None,
        files: dict[str, str] | None = None,
    ) -> dict:
        files = files or {}
        paths = {item["path"] for item in tree}
        lower_paths = {path.lower() for path in paths}
        readme_text = (readme or "").strip()

        def has_path(*needles: str) -> bool:
            return any(any(needle in path for needle in needles) for path in lower_paths)

        def has_file(*names: str) -> bool:
            lower_names = {name.lower() for name in names}
            return any(path.rsplit("/", 1)[-1].lower() in lower_names for path in lower_paths)

        def has_prefix(*prefixes: str) -> bool:
            return any(path.startswith(prefixes) for path in lower_paths)

        checks = {
            "readme": bool(readme_text) or has_file("README.md", "README", "README.rst"),
            "license": has_file("LICENSE", "LICENSE.md", "LICENSE.txt"),
            "contributing_guide": has_file("CONTRIBUTING.md", "CONTRIBUTING.rst"),
            "security_policy": has_path(".github/security.md", "security.md"),
            "issue_templates": has_prefix(".github/issue_template"),
            "pull_request_template": has_file("PULL_REQUEST_TEMPLATE.md", "pull_request_template.md") or has_path(".github/pull_request_template"),
            "code_owners": has_file("CODEOWNERS") or has_path(".github/codeowners"),
            "docker": "Docker" in tech_stack.get("containers", []) or has_file("Dockerfile"),
            "docker_compose": has_file("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"),
            "ci_cd": bool(tech_stack.get("ci_cd")) or has_prefix(".github/workflows"),
            "tests": has_prefix("tests", "test", "__tests__", "spec", "testing")
            or any(path.endswith(("_test.py", ".test.ts", ".test.js", ".spec.ts", ".spec.js")) for path in lower_paths),
            "wiki": bool(metadata.get("has_wiki", False)),
            "discussions": bool(metadata.get("has_discussions", False)),
            "funding": has_file("FUNDING.yml", "FUNDING.yaml", "FUNDING.md"),
            "releases": len(releases) > 0,
            "issues_enabled": metadata.get("has_issues", False),
        }

        weights = {
            "readme": 14,
            "license": 8,
            "contributing_guide": 8,
            "security_policy": 6,
            "issue_templates": 4,
            "pull_request_template": 4,
            "code_owners": 4,
            "docker": 8,
            "docker_compose": 4,
            "ci_cd": 12,
            "tests": 16,
            "wiki": 3,
            "discussions": 3,
            "funding": 2,
            "releases": 4,
            "issues_enabled": 4,
        }

        earned = sum(weights[name] for name, passed in checks.items() if passed)
        total = sum(weights.values())
        score = round((earned / total) * 100) if total else 0

        component_scores = {
            "documentation": self._group_score(checks, weights, ["readme", "license", "contributing_guide", "security_policy"]),
            "governance": self._group_score(checks, weights, ["issue_templates", "pull_request_template", "code_owners", "issues_enabled"]),
            "automation": self._group_score(checks, weights, ["ci_cd", "docker", "docker_compose"]),
            "quality": self._group_score(checks, weights, ["tests"]),
            "community": self._group_score(checks, weights, ["wiki", "discussions", "funding"]),
            "release_management": self._group_score(checks, weights, ["releases"]),
        }

        missing_recommendations = []
        if not checks["readme"]:
            missing_recommendations.append("Add a README with a concise project overview.")
        if not checks["license"]:
            missing_recommendations.append("Add a LICENSE file to clarify usage rights.")
        if not checks["contributing_guide"]:
            missing_recommendations.append("Add CONTRIBUTING guidelines for contributors.")
        if not checks["security_policy"]:
            missing_recommendations.append("Add a SECURITY policy for vulnerability reporting.")
        if not checks["issue_templates"]:
            missing_recommendations.append("Add issue templates to standardize bug reports and feature requests.")
        if not checks["pull_request_template"]:
            missing_recommendations.append("Add a pull request template to standardize submissions.")
        if not checks["code_owners"]:
            missing_recommendations.append("Add CODEOWNERS for review routing and ownership clarity.")
        if not checks["ci_cd"]:
            missing_recommendations.append("Add CI workflows to automate validation.")
        if not checks["tests"]:
            missing_recommendations.append("Add automated tests to protect key behaviors.")
        if not checks["docker"]:
            missing_recommendations.append("Add a Dockerfile for reproducible builds and deployment.")
        if not checks["releases"]:
            missing_recommendations.append("Publish releases or tags to improve version traceability.")

        if score >= 90:
            overall_status = "Excellent"
        elif score >= 75:
            overall_status = "Good"
        elif score >= 60:
            overall_status = "Fair"
        else:
            overall_status = "Needs Improvement"

        return {
            "score": score,
            "health": overall_status,
            "overall_status": overall_status,
            "checks": checks,
            "component_scores": component_scores,
            "missing_recommendations": missing_recommendations,
        }

    def _group_score(self, checks: dict[str, bool], weights: dict[str, int], names: list[str]) -> int:
        total = sum(weights.get(name, 0) for name in names)
        if not total:
            return 0
        earned = sum(weights.get(name, 0) for name in names if checks.get(name))
        return round((earned / total) * 100)
