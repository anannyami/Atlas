from pydantic import BaseModel, Field


class ResponseValidationResult(BaseModel):
    passed: bool
    overall_score: float = Field(ge=0.0, le=1.0)
    word_count: int = Field(ge=0)
    missing_sections: list[str] = Field(default_factory=list)
    missing_repository_evidence: list[str] = Field(default_factory=list)
    missing_engineering_observations: list[str] = Field(default_factory=list)
    generic_reasoning: bool = False
    hallucination_risk: float = Field(ge=0.0, le=1.0)
    followup_continuity: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    category_scores: dict[str, float] = Field(default_factory=dict)
    evidence_matches: list[str] = Field(default_factory=list)
    synthesized_areas: list[str] = Field(default_factory=list)
