from pydantic import BaseModel
from typing import Literal
from pydantic import BaseModel

class RepositoryTreeNode(BaseModel):
    name: str
    path: str
    type: Literal["file", "directory"]
    children: list["RepositoryTreeNode"] = []

RepositoryTreeNode.model_rebuild()

class StructureAnalysis(BaseModel):
    total_files: int
    total_directories: int
    max_depth: int
    major_directories: list[str]


class TechStackAnalysis(BaseModel):
    languages: list[str]

    frontend: list[str]
    backend: list[str]

    database: list[str]

    cloud: list[str]

    ci_cd: list[str]

    package_managers: list[str]

    mobile: list[str]

    containers: list[str]

class ArchitectureAnalysis(BaseModel):
    style: str

    applications: list[str]

    workspace: list[str]

    modules: list[str]

    deployment: list[str]


class AnalysisResponse(BaseModel):
    repository: RepositoryInfo
    structure: StructureAnalysis
    tech_stack: TechStackAnalysis
    architecture: ArchitectureAnalysis
    health: HealthAnalysis
    activity: ActivityAnalysis
    classification: ProjectClassification
    summary: RepositorySummary

class RepositorySummary(BaseModel):
    overview: str

class ProjectClassification(BaseModel):
    project_type: str

class HealthAnalysis(BaseModel):
    score: int
    checks: dict[str, bool]

class ActivityAnalysis(BaseModel):
    stars: int
    forks: int
    watchers: int
    open_issues: int

    recent_commits: int
    recent_pull_requests: int
    recent_issues: int

    releases: int
    last_commit_days: int | None

    community_size: str
    activity_level: str
    maintenance_status: str
    repository_maturity: str

class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    owner: str
    owner_avatar: str
    description: str | None
    html_url: str
    default_branch: str
    language: str | None
    topics: list[str]
    stars: int
    forks: int
    watchers: int
    open_issues: int
    created_at: str
    updated_at: str