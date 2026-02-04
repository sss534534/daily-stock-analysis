from fastapi import APIRouter, HTTPException
from app.models.investment_tool import (
    InvestmentGoal,
    AssetAllocation,
    InvestmentPortfolio,
    InvestmentReview,
    InvestmentPlan,
    CashFlow,
    InvestmentToolResponse
)
from typing import List
from datetime import date, timedelta
import random

router = APIRouter()

# 模拟数据存储
investment_goals = []
asset_allocations = []
investment_portfolios = []
investment_reviews = []
investment_plans = []
cash_flows = []

# 生成模拟现金流数据
def generate_cash_flows():
    flows = []
    today = date.today()
    
    for i in range(12):
        # 计算正确的月份和年份
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        month_date = date(year, month, 1)
        
        income = random.uniform(8000, 12000)
        expenses = random.uniform(5000, 8000)
        investment = random.uniform(1000, 3000)
        savings = income - expenses - investment
        
        flows.append(CashFlow(
            id=i + 1,
            month=month_date,
            income=round(income, 2),
            expenses=round(expenses, 2),
            investment=round(investment, 2),
            savings=round(savings, 2)
        ))
    
    return flows

# 初始化模拟数据
def init_mock_data():
    global investment_goals, asset_allocations, investment_portfolios, investment_reviews, investment_plans, cash_flows
    
    if not investment_goals:
        # 创建投资目标
        investment_goals = [
            InvestmentGoal(
                id=1,
                title="退休储蓄",
                target_amount=1000000,
                time_horizon=20,
                risk_tolerance="medium",
                current_amount=100000,
                monthly_contribution=3000,
                start_date=date(2024, 1, 1),
                description="为20年后的退休生活储蓄"
            ),
            InvestmentGoal(
                id=2,
                title="子女教育",
                target_amount=500000,
                time_horizon=15,
                risk_tolerance="medium",
                current_amount=50000,
                monthly_contribution=1500,
                start_date=date(2024, 1, 1),
                description="为子女的大学教育储蓄"
            )
        ]
        
        # 创建资产配置
        asset_allocations = [
            AssetAllocation(
                id=1,
                goal_id=1,
                cash=10,
                stocks=60,
                bonds=20,
                real_estate=5,
                commodities=3,
                alternative=2,
                risk_score=65
            ),
            AssetAllocation(
                id=2,
                goal_id=2,
                cash=15,
                stocks=50,
                bonds=30,
                real_estate=3,
                commodities=1,
                alternative=1,
                risk_score=55
            )
        ]
        
        # 创建投资组合
        investment_portfolios = [
            InvestmentPortfolio(
                id=1,
                goal_id=1,
                name="退休投资组合",
                assets=[
                    {"name": "沪深300ETF", "type": "stock", "weight": 30, "return": 0.08},
                    {"name": "中证500ETF", "type": "stock", "weight": 20, "return": 0.10},
                    {"name": "国债ETF", "type": "bond", "weight": 20, "return": 0.03},
                    {"name": "企业债ETF", "type": "bond", "weight": 10, "return": 0.05},
                    {"name": "货币基金", "type": "cash", "weight": 10, "return": 0.02},
                    {"name": "黄金ETF", "type": "commodity", "weight": 5, "return": 0.04},
                    {"name": "房地产REITs", "type": "real_estate", "weight": 5, "return": 0.06}
                ],
                risk_level="medium",
                expected_return=0.065
            ),
            InvestmentPortfolio(
                id=2,
                goal_id=2,
                name="教育投资组合",
                assets=[
                    {"name": "沪深300ETF", "type": "stock", "weight": 25, "return": 0.08},
                    {"name": "中证500ETF", "type": "stock", "weight": 15, "return": 0.10},
                    {"name": "国债ETF", "type": "bond", "weight": 30, "return": 0.03},
                    {"name": "企业债ETF", "type": "bond", "weight": 10, "return": 0.05},
                    {"name": "货币基金", "type": "cash", "weight": 15, "return": 0.02},
                    {"name": "黄金ETF", "type": "commodity", "weight": 3, "return": 0.04},
                    {"name": "房地产REITs", "type": "real_estate", "weight": 2, "return": 0.06}
                ],
                risk_level="low-medium",
                expected_return=0.05
            )
        ]
        
        # 创建投资回顾
        investment_reviews = [
            InvestmentReview(
                id=1,
                portfolio_id=1,
                review_date=date(2024, 12, 31),
                performance=0.085,
                notes="2024年投资组合表现良好，超过预期收益",
                recommended_actions=[
                    "保持当前资产配置",
                    "考虑增加国际市场 exposure",
                    "定期再平衡"
                ]
            ),
            InvestmentReview(
                id=2,
                portfolio_id=2,
                review_date=date(2024, 12, 31),
                performance=0.062,
                notes="教育投资组合表现符合预期",
                recommended_actions=[
                    "保持保守配置",
                    "增加每月定投金额"
                ]
            )
        ]
        
        # 创建投资计划
        investment_plans = [
            InvestmentPlan(
                id=1,
                goal_id=1,
                frequency="monthly",
                amount=3000,
                start_date=date(2024, 1, 1),
                next_investment_date=date.today() + timedelta(days=30)
            ),
            InvestmentPlan(
                id=2,
                goal_id=2,
                frequency="monthly",
                amount=1500,
                start_date=date(2024, 1, 1),
                next_investment_date=date.today() + timedelta(days=30)
            )
        ]
        
        # 生成现金流数据
        cash_flows = generate_cash_flows()

# 获取投资工具数据
@router.get("", response_model=InvestmentToolResponse)
async def get_investment_tool_data():
    init_mock_data()
    
    return InvestmentToolResponse(
        goals=investment_goals,
        asset_allocations=asset_allocations,
        portfolios=investment_portfolios,
        reviews=investment_reviews,
        plans=investment_plans,
        cash_flows=cash_flows
    )

# 获取投资目标列表
@router.get("/goals", response_model=List[InvestmentGoal])
async def get_investment_goals():
    init_mock_data()
    return investment_goals

# 添加投资目标
@router.post("/goals", response_model=InvestmentGoal)
async def add_investment_goal(goal: InvestmentGoal):
    init_mock_data()
    
    new_id = len(investment_goals) + 1
    new_goal = goal.model_copy()
    new_goal.id = new_id
    
    investment_goals.append(new_goal)
    return new_goal

# 更新投资目标
@router.put("/goals/{goal_id}", response_model=InvestmentGoal)
async def update_investment_goal(goal_id: int, goal: InvestmentGoal):
    init_mock_data()
    
    for i, existing_goal in enumerate(investment_goals):
        if existing_goal.id == goal_id:
            updated_goal = goal.model_copy()
            updated_goal.id = goal_id
            investment_goals[i] = updated_goal
            return updated_goal
    
    raise HTTPException(status_code=404, detail="Investment goal not found")

# 删除投资目标
@router.delete("/goals/{goal_id}")
async def delete_investment_goal(goal_id: int):
    init_mock_data()
    
    global investment_goals
    investment_goals = [goal for goal in investment_goals if goal.id != goal_id]
    return {"message": "Investment goal deleted successfully"}

# 获取资产配置
@router.get("/asset-allocation", response_model=List[AssetAllocation])
async def get_asset_allocations():
    init_mock_data()
    return asset_allocations

# 更新资产配置
@router.put("/asset-allocation/{allocation_id}", response_model=AssetAllocation)
async def update_asset_allocation(allocation_id: int, allocation: AssetAllocation):
    init_mock_data()
    
    for i, existing_allocation in enumerate(asset_allocations):
        if existing_allocation.id == allocation_id:
            updated_allocation = allocation.model_copy()
            updated_allocation.id = allocation_id
            asset_allocations[i] = updated_allocation
            return updated_allocation
    
    raise HTTPException(status_code=404, detail="Asset allocation not found")

# 获取投资组合
@router.get("/portfolios", response_model=List[InvestmentPortfolio])
async def get_investment_portfolios():
    init_mock_data()
    return investment_portfolios

# 获取投资回顾
@router.get("/reviews", response_model=List[InvestmentReview])
async def get_investment_reviews():
    init_mock_data()
    return investment_reviews

# 获取投资计划
@router.get("/plans", response_model=List[InvestmentPlan])
async def get_investment_plans():
    init_mock_data()
    return investment_plans

# 获取现金流数据
@router.get("/cash-flows", response_model=List[CashFlow])
async def get_cash_flows():
    init_mock_data()
    return cash_flows

# 获取投资建议
@router.get("/recommendations")
async def get_investment_recommendations():
    init_mock_data()
    
    recommendations = [
        {
            "title": "军规1: 设定长期目标",
            "content": "基于您的风险承受能力和时间 horizon，建议设定合理的长期投资目标。",
            "action": "使用投资目标工具创建详细的投资计划。"
        },
        {
            "title": "军规2: 永不满仓",
            "content": "建议保持10-20%的现金储备，以应对市场波动和把握投资机会。",
            "action": "调整资产配置，确保适当的现金比例。"
        },
        {
            "title": "军规3: 均衡配置",
            "content": "构建多元化的投资组合，降低单一资产风险。",
            "action": "检查并优化您的资产配置比例。"
        },
        {
            "title": "军规4: 定期复盘",
            "content": "建议每季度对投资组合进行一次全面回顾和再平衡。",
            "action": "使用投资回顾工具记录和分析投资表现。"
        },
        {
            "title": "军规5: 稳定心态",
            "content": "避免市场情绪影响，坚持长期投资策略。",
            "action": "设置止损和止盈点，减少情绪化决策。"
        },
        {
            "title": "军规6: 定期投入",
            "content": "采用定期定额投资策略，平滑市场波动风险。",
            "action": "设置每月自动投资计划。"
        },
        {
            "title": "军规7: 保持现金流",
            "content": "确保有足够的应急资金，避免因流动性问题被迫卖出资产。",
            "action": "使用现金流工具分析和管理个人财务状况。"
        }
    ]
    
    return recommendations
