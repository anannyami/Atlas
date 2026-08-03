from pydantic import BaseModel


class FolderIntelligence(BaseModel):
    path: str

    purpose: str

    summary: str

    contains: list[str]

    dependencies: list[str]

    dependents: list[str]

    importance: str

    interactions: list[str]


class FolderKnowledge(BaseModel):
    folders: list[FolderIntelligence]