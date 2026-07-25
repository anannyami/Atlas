from typing import Any


class ArchitectureAnalyzer:
    """
    Detects the architectural organization of a repository.

    This analyzer answers questions like:

    • Is this a monorepo?
    • Does it contain web/mobile/desktop apps?
    • Does it use workspaces?
    • Does it contain shared libraries?
    • How is deployment organized?
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
            path.lower()
            for path in paths
        }

        result = {
            "style": "Standard Repository",
            "applications": [],
            "workspace": [],
            "modules": [],
            "deployment": [],
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

        def add(category: str, value: str):
            if value not in result[category]:
                result[category].append(value)

        # --------------------------------------------------
        # Applications
        # --------------------------------------------------

        if any(
            path.startswith(("web/", "frontend/", "client/"))
            for path in lower_paths
        ):
            add("applications", "Web")

        if any(
            path.startswith(("mobile/", "android/", "ios/"))
            for path in lower_paths
        ):
            add("applications", "Mobile")

        if any(
            path.startswith(("desktop/", "electron/", "tauri/"))
            for path in lower_paths
        ):
            add("applications", "Desktop")

        if any(
            path.startswith(("cli/", "cmd/", "bin/"))
            for path in lower_paths
        ):
            add("applications", "CLI")

        # --------------------------------------------------
        # Workspace Detection
        # --------------------------------------------------

        cargo_workspace = get_file("Cargo.toml")

        if "[workspace]" in cargo_workspace:
            add("workspace", "Cargo Workspace")

        if "pnpm-workspace.yaml" in lower_paths:
            add("workspace", "pnpm Workspace")

        if "package.json" in lower_paths:

            package_json = get_file("package.json")

            if '"workspaces"' in package_json:
                add("workspace", "npm Workspaces")

        # --------------------------------------------------
        # Modules
        # --------------------------------------------------

        if any(path.startswith("packages/") for path in lower_paths):
            add("modules", "Packages")

        if any(path.startswith("crates/") for path in lower_paths):
            add("modules", "Rust Crates")

        if any(path.startswith("libs/") for path in lower_paths):
            add("modules", "Libraries")

        if any(path.startswith("shared/") for path in lower_paths):
            add("modules", "Shared Libraries")

        if any(path.startswith("common/") for path in lower_paths):
            add("modules", "Common Modules")

        # --------------------------------------------------
        # Deployment
        # --------------------------------------------------

        if any(
            "dockerfile" in path
            for path in lower_paths
        ):
            add("deployment", "Docker")

        if any(
            "docker-compose" in path or "compose.yml" in path
            for path in lower_paths
        ):
            add("deployment", "Docker Compose")

        if any(
            "kubernetes" in path or "k8s" in path
            for path in lower_paths
        ):
            add("deployment", "Kubernetes")

        if "vercel.json" in lower_paths:
            add("deployment", "Vercel")

        if "netlify.toml" in lower_paths:
            add("deployment", "Netlify")

        # --------------------------------------------------
        # Repository Style
        # --------------------------------------------------

        score = 0

        if len(result["applications"]) > 1:
            score += 1

        if len(result["workspace"]) > 0:
            score += 1

        if len(result["modules"]) > 0:
            score += 1

        if any(
            path.startswith(("apps/", "packages/", "crates/"))
            for path in lower_paths
        ):
            score += 1

        if score >= 2:
            result["style"] = "Monorepo"

        # --------------------------------------------------
        # Sort
        # --------------------------------------------------

        for key in (
            "applications",
            "workspace",
            "modules",
            "deployment",
        ):
            result[key] = sorted(result[key])

        return result