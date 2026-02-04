from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

# 数据库模型
class StockDB(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    change = Column(Float)
    changePercent = Column(Float)
    volume = Column(Integer)
    marketCap = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StockHistoryDB(Base):
    __tablename__ = "stock_histories"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String, index=True)
    date = Column(String)
    price = Column(Float)
    volume = Column(Integer)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)

# Pydantic模型（用于API响应）
class Stock(BaseModel):
    id: str
    code: str
    name: str
    price: float
    change: float
    changePercent: float
    volume: int
    marketCap: int

    class Config:
        from_attributes = True

class StockHistory(BaseModel):
    date: str
    price: float
    volume: int
    high: float
    low: float
    open: float

    class Config:
        from_attributes = True
