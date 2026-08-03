from pydantic import BaseModel

from models.analysis import (
    RepositoryInfo,
    StructureAnalysis,
    TechStackAnalysis,
    ArchitectureAnalysis,
    HealthAnalysis,
    ActivityAnalysis,
    ProjectClassification,
    RepositorySummary,
    PurposeAnalysis,
)

from models.intelligence import RepositoryKnowledge
from models.architecture_blueprint import ArchitectureBlueprint
from models.repository_identity import RepositoryIdentity
from models.analysis import ProductIdentity


class AnalysisResponse(BaseModel):
    repository: RepositoryInfo

    structure: StructureAnalysis

    tech_stack: TechStackAnalysis

    architecture: ArchitectureAnalysis

    health: HealthAnalysis

    activity: ActivityAnalysis

    classification: ProjectClassification

    summary: RepositorySummary

    purpose: PurposeAnalysis

    knowledge: RepositoryKnowledge

    blueprint: ArchitectureBlueprint

    product_identity: ProductIdentity | None = None

    repository_identity: RepositoryIdentity | None = None