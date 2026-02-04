from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class InvestmentGoal(BaseModel):
    id: Optional[int] = None
    title: str
    target_amount: float
    time_horizon: int  # 年
    risk_tolerance: str  # low, medium, high
    current_amount: float = 0.0
    monthly_contribution: float = 0.0
    start_date: date = date.today()
    description: Optional[str] = None

class AssetAllocation(BaseModel):
    id: Optional[int] = None
    goal_id: Optional[int] = None
    cash: float = 0.0
    stocks: float = 0.0
    bonds: float = 0.0
    real_estate: float = 0.0
    commodities: float = 0.0
    alternative: float = 0.0
    risk_score: Optional[float] = None

class InvestmentPortfolio(BaseModel):
    id: Optional[int] = None
    goal_id: Optional[int] = None
    name: str
    assets: List[Dict[str, Any]]
    risk_level: str
    expected_return: Optional[float] = None

class InvestmentReview(BaseModel):
    id: Optional[int] = None
    portfolio_id: Optional[int] = None
    review_date: date = date.today()
    performance: float
    notes: Optional[str] = None
    recommended_actions: Optional[List[str]] = None

class InvestmentPlan(BaseModel):
    id: Optional[int] = None
    goal_id: Optional[int] = None
    frequency: str  # monthly, quarterly, yearly
    amount: float
    start_date: date = date.today()
    next_investment_date: Optional[date] = None

class CashFlow(BaseModel):
    id: Optional[int] = None
    month: date
    income: float
    expenses: float
    investment: float
    savings: float

class InvestmentToolResponse(BaseModel):
    goals: List[InvestmentGoal]
    asset_allocations: List[AssetAllocation]
    portfolios: List[InvestmentPortfolio]
    reviews: List[InvestmentReview]
    plans: List[InvestmentPlan]
    cash_flows: List[CashFlow]
