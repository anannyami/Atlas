from pydantic import BaseModel


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