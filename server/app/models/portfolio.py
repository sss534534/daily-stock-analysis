from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

# 数据库模型
class PositionDB(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    stockCode = Column(String, index=True)
    stockName = Column(String)
    shares = Column(Integer)
    buyPrice = Column(Float)
    currentPrice = Column(Float)
    buyDate = Column(String)
    profit = Column(Float)
    profitPercent = Column(Float)
    totalValue = Column(Float)
    cost = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic模型（用于API响应）
class Position(BaseModel):
    id: str
    stockCode: str
    stockName: str
    shares: int
    buyPrice: float
    currentPrice: float
    buyDate: str
    profit: float
    profitPercent: float
    totalValue: float
    cost: float

    class Config:
        from_attributes = True

class PortfolioStats(BaseModel):
    totalCost: float
    totalValue: float
    totalProfit: float
    totalProfitPercent: float
    positionCount: int

class PositionCreate(BaseModel):
    stockCode: str
    stockName: str
    shares: int
    buyPrice: float
    buyDate: str

class PositionUpdate(BaseModel):
    shares: int | None = None
    buyPrice: float | None = None
