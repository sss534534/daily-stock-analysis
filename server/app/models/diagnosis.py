from pydantic import BaseModel
from typing import List

class DiagnosisResult(BaseModel):
    stockCode: str
    stockName: str
    technicalScore: int
    fundamentalScore: int
    marketScore: int
    overallScore: int
    rating: str
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str
