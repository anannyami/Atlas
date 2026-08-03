from pydantic import BaseModel, Field

from models.analysis import (
    RepositoryInfo,
    RepositoryTreeNode,
    StructureAnalysis,
    TechStackAnalysis,
    ArchitectureAnalysis,
    HealthAnalysis,
    ActivityAnalysis,
    RepositorySummary,
    PurposeAnalysis,
    ProjectClassification,
)
from models.github_tree import GitHubTreeItem


class RepositoryKnowledge(BaseModel):
    """
    Canonical repository knowledge object.

    Every Phase 4 feature consumes this object.
    """

    repository: RepositoryInfo

    tree: list[RepositoryTreeNode] = Field(default_factory=list)

    summary: RepositorySummary | None = None

    purpose: PurposeAnalysis | None = None

    classification: ProjectClassification | None = None

    structure: StructureAnalysis

    tech_stack: TechStackAnalysis

    architecture: ArchitectureAnalysis

    health: HealthAnalysis

    activity: ActivityAnalysis

    contributors: list[dict] = Field(default_factory=list)

    branches: list[dict] = Field(default_factory=list)

    releases: list[dict] = Field(default_factory=list)

    issues: list[dict] = Field(default_factory=list)

    pull_requests: list[dict] = Field(default_factory=list)

    readme: str | None = None

    capabilities: list[str] = Field(default_factory=list)

    dependencies: list[str] = Field(default_factory=list)

    major_folders: list[str] = Field(default_factory=list)

    evidence: list[dict] = Field(default_factory=list)