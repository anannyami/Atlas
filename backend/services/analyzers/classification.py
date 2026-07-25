from typing import Any


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
    ) -> dict:

        paths = {
            item["path"]
            for item in tree
        }

        frontend = tech_stack.get("frontend")
        backend = tech_stack.get("backend")

        project_type = "Unknown"
        priority = 0


        def set_project_type(name: str, score: int):
            nonlocal project_type, priority

            if score > priority:
                project_type = name
                priority = score

        #
        # ----------------------------------------
        # Full Stack
        # ----------------------------------------
        #

        if frontend and backend:
            set_project_type(
                "Full Stack Application",
                100,
            )

        #
        # ----------------------------------------
        # Frontend
        # ----------------------------------------
        #

        elif frontend:
            set_project_type(
                "Frontend Application",
                90,
            )

        #
        # ----------------------------------------
        # Backend
        # ----------------------------------------
        #

        elif backend:
            set_project_type(
                "Backend Service",
                95,
            )

        #
        # ----------------------------------------
        # Machine Learning
        # ----------------------------------------
        #

        ml_dirs = {
            "models",
            "notebooks",
            "dataset",
            "datasets",
        }

        if any(
            path.startswith(tuple(ml_dirs))
            for path in paths
        ):
            set_project_type(
                "Machine Learning Project",
                85,
            )

        #
        # ----------------------------------------
        # Library
        # ----------------------------------------
        #

        if (
            "setup.py" in paths
            or "pyproject.toml" in paths
        ) and any(
            path.startswith("examples/")
            for path in paths
        ):
            set_project_type(
                "Library",
                70,
            )

        #
        # ----------------------------------------
        # CLI Tool
        # ----------------------------------------
        #

        if any(
            path.endswith(("cli.py", "main.py"))
            for path in paths
        ):
            set_project_type(
                "CLI Tool",
                60,
            )

        #
        # ----------------------------------------
        # DevOps
        # ----------------------------------------
        #

        infra_files = {
            "terraform",
            ".github",
            "ansible",
            "helm",
            "charts",
        }

        if any(
            keyword in path
            for keyword in infra_files
            for path in paths
        ):
            set_project_type(
                "DevOps / Infrastructure",
                50,
            )

        return {
            "project_type": project_type,
        }