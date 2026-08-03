from pydantic import BaseModel, Field
from typing import List


class ArchitectureLayer(BaseModel):
    name: str
    type: str
    directories: List[str] = Field(default_factory=list)


class ComponentNode(BaseModel):
    id: str
    name: str
    category: str
    directory: str


class DependencyEdge(BaseModel):
    source: str
    target: str
    relation: str


class CommunicationPath(BaseModel):
    source: str
    target: str
    protocol: str


class DataFlowStep(BaseModel):
    order: int
    source: str
    target: str
    description: str


class ExternalService(BaseModel):
    name: str
    type: str


class ArchitectureBlueprint(BaseModel):
    architecture_type: str
    confidence: float

    layers: List[ArchitectureLayer] = Field(default_factory=list)

    components: List[ComponentNode] = Field(default_factory=list)

    dependencies: List[DependencyEdge] = Field(default_factory=list)

    communication: List[CommunicationPath] = Field(default_factory=list)

    entrypoints: List[str] = Field(default_factory=list)

    external_services: List[ExternalService] = Field(default_factory=list)

    data_flow: List[DataFlowStep] = Field(default_factory=list)