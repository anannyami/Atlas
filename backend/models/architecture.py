from pydantic import BaseModel


class ArchitectureComponent(BaseModel):
    id: str
    name: str
    type: str
    description: str


class ArchitectureConnection(BaseModel):
    source: str
    target: str
    relationship: str


class ArchitectureLayer(BaseModel):
    name: str
    components: list[str]


class ArchitectureBlueprint(BaseModel):
    pattern: str
    summary: str

    layers: list[ArchitectureLayer]

    components: list[ArchitectureComponent]

    connections: list[ArchitectureConnection]

    entrypoints: list[str]

    data_flow: list[str]

    external_dependencies: list[str]

    confidence: float