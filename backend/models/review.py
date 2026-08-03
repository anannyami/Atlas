from pydantic import BaseModel


class ReviewCategory(BaseModel):
    score: int
    summary: str
    evidence: list[str]


class AIRepositoryReview(BaseModel):
    strengths: list[str]

    weaknesses: list[str]

    architecture: ReviewCategory

    maintainability: ReviewCategory

    scalability: ReviewCategory

    documentation: ReviewCategory

    security: ReviewCategory

    developer_experience: ReviewCategory

    overall_score: int