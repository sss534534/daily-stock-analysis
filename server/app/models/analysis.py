from pydantic import BaseModel
from typing import List, Optional

class AIRecommendation(BaseModel):
    type: str
    confidence: float
    reason: str
    targetPrice: Optional[float] = None
    stopLoss: Optional[float] = None
    timeframe: str

class RiskFactor(BaseModel):
    name: str
    impact: float
    description: str

class RiskAnalysis(BaseModel):
    level: str
    score: float
    factors: List[RiskFactor]

class ChanPivot(BaseModel):
    type: str
    price: float
    date: str

class ChanBuyPoint(BaseModel):
    price: float
    date: str
    confidence: float

class ChanSellPoint(BaseModel):
    price: float
    date: str
    confidence: float

class ChanTheoryAnalysis(BaseModel):
    trend: str
    level: int
    pivots: List[ChanPivot]
    segments: List[str]
    buyPoints: List[ChanBuyPoint]
    sellPoints: List[ChanSellPoint]

class LivermorePivotalPoint(BaseModel):
    price: float
    type: str

class LivermoreAnalysis(BaseModel):
    marketPhase: str
    pivotalPoints: List[LivermorePivotalPoint]
    trendStrength: float
    volumeAnalysis: str
    recommendation: str
