from pydantic import BaseModel


class ImprovementOpportunity(BaseModel):
    title: str

    impact: str

    difficulty: str

    explanation: str

    evidence: list[str]


class ImprovementAnalysis(BaseModel):
    opportunities: list[ImprovementOpportunity]