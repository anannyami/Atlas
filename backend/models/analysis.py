from typing import Literal

from pydantic import BaseModel, Field


class DetectedSignal(BaseModel):
    name: str
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)


class DirectoryInsight(BaseModel):
    path: str
    file_count: int = 0
    depth: int = 0


class RepositoryTreeNode(BaseModel):
    name: str
    path: str
    type: Literal["file", "directory"]
    children: list["RepositoryTreeNode"] = Field(default_factory=list)


RepositoryTreeNode.model_rebuild()


class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    owner: str
    owner_avatar: str
    description: str | None
    html_url: str
    default_branch: str
    language: str |None
    topics: list[str]
    stars: int
    forks: int
    watchers: int
    open_issues: int
    created_at: str
    updated_at: str


class StructureAnalysis(BaseModel):
    total_files: int
    total_directories: int
    max_depth: int
    major_directories: list[str]
    largest_directories: list[DirectoryInsight] = Field(default_factory=list)
    deepest_paths: list[DirectoryInsight] = Field(default_factory=list)
    major_modules: list[str] = Field(default_factory=list)
    entry_points: list[str] = Field(default_factory=list)
    important_folders: list[str] = Field(default_factory=list)
    configuration_files: list[str] = Field(default_factory=list)
    root_technologies: list[str] = Field(default_factory=list)
    summary: str = ""


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

    frontend_frameworks: list[DetectedSignal] = Field(default_factory=list)
    backend_frameworks: list[DetectedSignal] = Field(default_factory=list)
    databases: list[DetectedSignal] = Field(default_factory=list)
    cloud: list[DetectedSignal] = Field(default_factory=list)
    authentication: list[DetectedSignal] = Field(default_factory=list)
    api_styles: list[DetectedSignal] = Field(default_factory=list)
    architecture_patterns: list[DetectedSignal] = Field(default_factory=list)
    organization: list[str] = Field(default_factory=list)

    confidence: float = 0.0
    summary: str = ""


class HealthAnalysis(BaseModel):
    score: int
    checks: dict[str, bool]
    component_scores: dict[str, int] = Field(default_factory=dict)
    missing_recommendations: list[str] = Field(default_factory=list)
    overall_status: str = ""


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
    commit_frequency: str = ""
    issue_frequency: str = ""
    pr_frequency: str = ""
    staleness: str = ""
    explanations: list[str] = Field(default_factory=list)


class RepositorySummary(BaseModel):
    overview: str
    purpose: str
    current_status: str
    highlights: list[str]
    source_factors: list[str] = Field(default_factory=list)


class ProjectClassification(BaseModel):
    project_type: str
    primary_classification: str = ""
    secondary_classifications: list[DetectedSignal] = Field(default_factory=list)
    confidence: float = 0.0


class PurposeAnalysis(BaseModel):
    what: str
    why: str
    audience: str
    problem: str
    capabilities: list[str]
    technology_story: str
    confidence: float


class ProductIdentity(BaseModel):
    category: str
    subcategory: str
    title: str
    summary: str
    confidence: float
    evidence: list[str]