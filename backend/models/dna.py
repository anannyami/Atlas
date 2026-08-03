from pydantic import BaseModel


class DNATrait(BaseModel):
    name: str
    confidence: float
    evidence: list[str]


class RepositoryDNA(BaseModel):
    engineering_style: str

    maturity: str

    traits: list[DNATrait]

    strengths: list[str]

    confidence: float