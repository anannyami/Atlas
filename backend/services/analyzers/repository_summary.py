from typing import Any


class RepositorySummaryAnalyzer:
    """
    Generates a human-readable repository summary by combining
    outputs from the other analyzers.
    """

    def analyze(
        self,
        metadata: dict[str, Any],
        tech_stack: dict,
        architecture: dict,
        health: dict,
        activity: dict,
    ) -> dict:

        languages = tech_stack["languages"]
        frontend = tech_stack["frontend"]
        backend = tech_stack["backend"]
        database = tech_stack["database"]

        style = architecture["style"]
        apps = architecture["applications"]

        sentences = []

        # --------------------------------------------------
        # Project Type
        # --------------------------------------------------

        if frontend and backend:
            sentences.append(
                f"This repository is a full-stack project built with "
                f"{', '.join(frontend)} and {', '.join(backend)}."
            )

        elif frontend:
            sentences.append(
                f"This repository is primarily a frontend application "
                f"built using {', '.join(frontend)}."
            )

        elif backend:
            sentences.append(
                f"This repository is primarily a backend service "
                f"implemented with {', '.join(backend)}."
            )

        elif languages:
            sentences.append(
                f"This project is mainly written in "
                f"{', '.join(languages[:3])}."
            )

        # --------------------------------------------------
        # Architecture
        # --------------------------------------------------

        if style == "Monorepo":

            app_text = ", ".join(apps) if apps else "multiple applications"

            sentences.append(
                f"It follows a monorepo architecture containing {app_text}."
            )

        else:

            sentences.append(
                "The repository follows a standard project structure."
            )

        # --------------------------------------------------
        # Database
        # --------------------------------------------------

        if database:

            sentences.append(
                f"It uses {', '.join(database)} for data storage or caching."
            )

        # --------------------------------------------------
        # Activity
        # --------------------------------------------------

        activity_level = activity["activity_level"]

        maturity = activity["repository_maturity"]

        sentences.append(
            f"The project is currently {activity_level.lower()}ly active "
            f"and is considered {maturity.lower()}."
        )

        # --------------------------------------------------
        # Health
        # --------------------------------------------------

        score = health["score"]

        if score >= 85:

            sentences.append(
                "Overall repository health is excellent with modern "
                "development practices."
            )

        elif score >= 70:

            sentences.append(
                "Overall repository health is good."
            )

        else:

            sentences.append(
                "Repository health could be improved."
            )

        return {
            "overview": " ".join(sentences)
        }