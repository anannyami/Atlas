from models.analysis import (
    RepositoryInfo,
    RepositorySummary,
    PurposeAnalysis,
    ProjectClassification,
    StructureAnalysis,
    TechStackAnalysis,
    HealthAnalysis,
    ActivityAnalysis,
)

from models.intelligence import (
    RepositoryKnowledge,
)


class IntelligenceEngine:
    """
    Builds the canonical RepositoryKnowledge object.

    This class performs aggregation only.
    No AI reasoning or scoring should happen here.
    """

    def build(
        self,
        *,
        repository: RepositoryInfo,
        summary: RepositorySummary,
        purpose: PurposeAnalysis,
        classification: ProjectClassification,
        structure: StructureAnalysis,
        tech_stack: TechStackAnalysis,
        health: HealthAnalysis,
        activity: ActivityAnalysis,
        readme: str | None,
    ) -> RepositoryKnowledge:

        capabilities = purpose.capabilities.copy()

        dependencies: list[str] = []

        major_folders = structure.major_directories.copy()

        return RepositoryKnowledge(
            repository=repository,
            summary=summary,
            purpose=purpose,
            classification=classification,
            structure=structure,
            tech_stack=tech_stack,
            health=health,
            activity=activity,
            readme=readme,
            capabilities=capabilities,
            dependencies=dependencies,
            major_folders=major_folders,
            evidence=[],
        )