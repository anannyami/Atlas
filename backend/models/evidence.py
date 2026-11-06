from pydantic import BaseModel


class RepositoryFileEvidence(BaseModel):
    path: str
    file_type: str
    start_line: int = 1
    end_line: int = 1
    text: str
    truncated: bool = False


class RepositoryEvidence(BaseModel):
    title: str
    description: str
    readme: str

    topics: list[str]

    frontend: list[str]
    backend: list[str]
    databases: list[str]
    cloud: list[str]
    cicd: list[str]

    architecture: dict

    structure: dict

    health: dict

    activity: dict