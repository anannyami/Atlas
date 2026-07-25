from pydantic import BaseModel

from models.analysis import AnalysisResponse


class AnalyzeRepositoryResponse(BaseModel):
    success: bool
    data: AnalysisResponse