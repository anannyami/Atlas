from pydantic import BaseModel

from models.analysis import (
    RepositoryInfo,
    StructureAnalysis,
    TechStackAnalysis,
    RepositorySummary,
    PurposeAnalysis,
    ProjectClassification,
    HealthAnalysis,
    ActivityAnalysis,
)


class KnowledgeEvidence(BaseModel):
    source: str
    details: str


class RepositoryKnowledge(BaseModel):
    """
    Canonical knowledge representation for a repository.

    Every Phase 4 feature consumes this model instead of
    reading GitHub data directly.
    """

    repository: RepositoryInfo

    summary: RepositorySummary

    purpose: PurposeAnalysis

    classification: ProjectClassification

    structure: StructureAnalysis

    tech_stack: TechStackAnalysis

    health: HealthAnalysis

    activity: ActivityAnalysis

    readme: str | None = None

    dependencies: list[str] = []

    capabilities: list[str] = []

    major_folders: list[str] = []

    evidence: list[KnowledgeEvidence] = []