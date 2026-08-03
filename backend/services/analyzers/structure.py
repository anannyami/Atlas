from collections import defaultdict
from typing import Any

from models.analysis import DirectoryInsight, RepositoryTreeNode


class StructureAnalyzer:
    """
    Analyzes the repository tree returned by GitHub's
    /git/trees/{branch}?recursive=1 endpoint.
    """

    def analyze(
        self,
        tree: list[dict[str, Any]],
        files: dict[str, str] | None = None,
        tech_stack: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        total_files = 0
        total_directories = 0
        max_depth = 0

        major_directories: set[str] = set()
        file_paths: list[str] = []
        directory_depths: dict[str, int] = {}
        directory_counts: dict[str, int] = defaultdict(int)

        files = files or {}
        tech_stack = tech_stack or {}

        configuration_filenames = {
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "pyproject.toml",
            "requirements.txt",
            "poetry.lock",
            "Pipfile",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "tsconfig.json",
            "vite.config.ts",
            "vite.config.js",
            "next.config.js",
            "next.config.ts",
            "next.config.mjs",
            "nuxt.config.ts",
            "nuxt.config.js",
            "angular.json",
            "astro.config.ts",
            "astro.config.mjs",
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
            "Dockerfile",
            "README.md",
        }

        important_folder_names = {
            "src",
            "app",
            "api",
            "services",
            "service",
            "models",
            "model",
            "controllers",
            "controller",
            "routes",
            "pages",
            "components",
            "lib",
            "core",
            "config",
            "backend",
            "frontend",
            "client",
            "server",
            "tests",
            "test",
            "docs",
            "packages",
            "modules",
            "shared",
            "common",
            "infra",
            "infrastructure",
        }

        entry_point_names = {
            "main.py",
            "app.py",
            "server.py",
            "manage.py",
            "index.js",
            "index.ts",
            "index.tsx",
            "main.ts",
            "main.tsx",
            "server.js",
            "server.ts",
            "app.ts",
            "app.tsx",
        }

        for item in tree:
            item_type = item.get("type")
            path = item.get("path", "")

            if item_type == "blob":
                total_files += 1
                file_paths.append(path)
            elif item_type == "tree":
                total_directories += 1

            parts = path.split("/") if path else []
            depth = max(len(parts) - 1, 0)

            if depth > max_depth:
                max_depth = depth

            if len(parts) > 1:
                major_directories.add(parts[0])

            if item_type == "blob" and len(parts) > 1:
                for index in range(1, len(parts)):
                    prefix = "/".join(parts[:index])
                    directory_counts[prefix] += 1

            if path:
                directory_depths[path] = depth

        def basename(path: str) -> str:
            return path.rsplit("/", 1)[-1].lower()

        def unique(values: list[str]) -> list[str]:
            return sorted(dict.fromkeys(values))

        detected_important_folders = sorted(
            {
                path.split("/")[0]
                for path in file_paths + [item.get("path", "") for item in tree]
                if path and path.split("/")[0].lower() in important_folder_names
            }
        )

        configuration_files = sorted(
            {
                basename(path)
                for path in file_paths + [item.get("path", "") for item in tree]
                if basename(path) in configuration_filenames
            }
        )

        entry_points = sorted(
            {
                path
                for path in file_paths
                if basename(path) in entry_point_names
            }
        )

        root_technologies: list[str] = []
        for category in ("languages", "frontend", "backend", "database", "cloud", "containers"):
            for value in tech_stack.get(category, []):
                if value not in root_technologies:
                    root_technologies.append(value)

        top_directories = sorted(
            directory_counts.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:8]

        largest_directories = [
            DirectoryInsight(
                path=path,
                file_count=count,
                depth=max(path.count("/"), 0),
            )
            for path, count in top_directories
        ]

        deepest_paths = [
            DirectoryInsight(
                path=path,
                file_count=1,
                depth=depth,
            )
            for path, depth in sorted(
                directory_depths.items(),
                key=lambda item: (-item[1], item[0].lower()),
            )[:8]
        ]

        module_candidates = []
        for prefix in (
            "apps",
            "packages",
            "modules",
            "services",
            "models",
            "controllers",
            "routes",
            "components",
            "api",
            "backend",
            "frontend",
            "client",
            "server",
            "shared",
            "common",
        ):
            if prefix in major_directories or any(path.startswith(prefix + "/") for path in file_paths):
                module_candidates.append(prefix)

        organization = unique(
            [
                "Package organization" if configuration_files else "",
                "Service layer" if any(path.startswith(("services/", "service/")) for path in file_paths) else "",
                "Model layer" if any(path.startswith(("models/", "model/", "domain/", "entities/")) for path in file_paths) else "",
                "Controller layer" if any(path.startswith(("controllers/", "controller/", "routes/", "handlers/")) for path in file_paths) else "",
                "Folder organization" if detected_important_folders else "",
            ]
        )

        summary_parts = []
        if major_directories:
            summary_parts.append(
                f"The repository is organized around {', '.join(sorted(major_directories)[:4])}."
            )
        if entry_points:
            summary_parts.append(
                f"Detected entry points include {', '.join(entry_points[:3])}."
            )
        if configuration_files:
            summary_parts.append(
                f"Key configuration files include {', '.join(configuration_files[:5])}."
            )
        if root_technologies:
            summary_parts.append(
                f"Root technologies include {', '.join(root_technologies[:5])}."
            )

        summary = " ".join(summary_parts)

        return {
            "total_files": total_files,
            "total_directories": total_directories,
            "max_depth": max_depth,
            "major_directories": sorted(major_directories),
            "largest_directories": [item.model_dump() for item in largest_directories],
            "deepest_paths": [item.model_dump() for item in deepest_paths],
            "major_modules": unique(module_candidates),
            "entry_points": entry_points,
            "important_folders": detected_important_folders,
            "configuration_files": configuration_files,
            "root_technologies": unique(root_technologies),
            "summary": summary,
        }


def build_repository_tree(tree: list) -> list[RepositoryTreeNode]:
    """
    Convert GitHub's flat recursive tree into a nested folder structure.
    """

    root = {}

    for item in tree:
        path_parts = item["path"].split("/")
        current = root

        for index, part in enumerate(path_parts):
            is_last = index == len(path_parts) - 1

            if part not in current:
                current[part] = {
                    "name": part,
                    "path": "/".join(path_parts[: index + 1]),
                    "type": "file"
                    if is_last and item["type"] == "blob"
                    else "directory",
                    "children": {},
                }

            current = current[part]["children"]

    def convert(node_dict):
        nodes = []

        for node in sorted(
            node_dict.values(),
            key=lambda x: (x["type"] == "file", x["name"].lower()),
        ):
            nodes.append(
                RepositoryTreeNode(
                    name=node["name"],
                    path=node["path"],
                    type=node["type"],
                    children=convert(node["children"]),
                )
            )

        return nodes

    return convert(root)
