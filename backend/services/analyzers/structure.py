from typing import Any

from models.analysis import RepositoryTreeNode


class StructureAnalyzer:
    """
    Analyzes the repository tree returned by GitHub's
    /git/trees/{branch}?recursive=1 endpoint.
    """

    def analyze(self, tree: list[dict[str, Any]]) -> dict[str, Any]:
        total_files = 0
        total_directories = 0
        max_depth = 0

        major_directories: set[str] = set()

        for item in tree:
            item_type = item.get("type")
            path = item.get("path", "")

            if item_type == "blob":
                total_files += 1
            elif item_type == "tree":
                total_directories += 1

            parts = path.split("/")

            depth = max(len(parts) - 1, 0)

            if depth > max_depth:
                max_depth = depth

            if len(parts) > 1:
                major_directories.add(parts[0])

        return {
            "total_files": total_files,
            "total_directories": total_directories,
            "max_depth": max_depth,
            "major_directories": sorted(major_directories),
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