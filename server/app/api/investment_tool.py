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
from typing import List, Dict, Any
from datetime import date, timedelta
import random
import numpy as np

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

# 资产配置优化算法
def optimize_asset_allocation(risk_tolerance: str, time_horizon: int) -> Dict[str, float]:
    """根据风险承受能力和时间周期优化资产配置"""
    
    # 基础配置模板
    base_allocations = {
        "low": {
            "cash": 20,
            "stocks": 30,
            "bonds": 40,
            "real_estate": 5,
            "commodities": 3,
            "alternative": 2
        },
        "medium": {
            "cash": 10,
            "stocks": 50,
            "bonds": 30,
            "real_estate": 5,
            "commodities": 3,
            "alternative": 2
        },
        "high": {
            "cash": 5,
            "stocks": 70,
            "bonds": 15,
            "real_estate": 5,
            "commodities": 3,
            "alternative": 2
        }
    }
    
    # 根据时间周期调整配置
    allocation = base_allocations.get(risk_tolerance, base_allocations["medium"]).copy()
    
    # 时间周期越长，权益类资产比例越高
    if time_horizon > 20:
        allocation["stocks"] += 10
        allocation["bonds"] -= 10
    elif time_horizon < 5:
        allocation["cash"] += 10
        allocation["stocks"] -= 10
    
    return allocation

# 现金流分析函数
def analyze_cash_flow(cash_flows: List[CashFlow]) -> Dict[str, Any]:
    """分析现金流数据，提供财务健康评估"""
    if not cash_flows:
        return {
            "monthly_average_income": 0,
            "monthly_average_expenses": 0,
            "monthly_average_savings": 0,
            "savings_rate": 0,
            "financial_health": "数据不足",
            "recommendations": []
        }
    
    # 计算平均值
    incomes = [flow.income for flow in cash_flows]
    expenses = [flow.expenses for flow in cash_flows]
    savings = [flow.savings for flow in cash_flows]
    
    avg_income = np.mean(incomes)
    avg_expenses = np.mean(expenses)
    avg_savings = np.mean(savings)
    
    # 计算储蓄率
    savings_rate = (avg_savings / avg_income) * 100 if avg_income > 0 else 0
    
    # 评估财务健康状况
    if savings_rate >= 30:
        financial_health = "优秀"
    elif savings_rate >= 20:
        financial_health = "良好"
    elif savings_rate >= 10:
        financial_health = "一般"
    elif savings_rate >= 0:
        financial_health = "需要改善"
    else:
        financial_health = "不健康"
    
    # 生成建议
    recommendations = []
    if savings_rate < 10:
        recommendations.append("建议增加收入或减少支出，提高储蓄率")
    if avg_expenses > avg_income * 0.7:
        recommendations.append("支出占比过高，建议控制日常开支")
    if avg_savings < 0:
        recommendations.append("出现负储蓄，需要立即调整财务计划")
    if savings_rate >= 20:
        recommendations.append("财务状况良好，可以考虑增加投资比例")
    
    return {
        "monthly_average_income": round(avg_income, 2),
        "monthly_average_expenses": round(avg_expenses, 2),
        "monthly_average_savings": round(avg_savings, 2),
        "savings_rate": round(savings_rate, 2),
        "financial_health": financial_health,
        "recommendations": recommendations
    }

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

# 获取优化的资产配置
@router.get("/optimize-asset-allocation")
async def get_optimized_asset_allocation(risk_tolerance: str, time_horizon: int):
    """根据风险承受能力和时间周期获取优化的资产配置"""
    if risk_tolerance not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="风险承受能力必须是 low、medium 或 high")
    
    if time_horizon <= 0:
        raise HTTPException(status_code=400, detail="时间周期必须大于0")
    
    optimized_allocation = optimize_asset_allocation(risk_tolerance, time_horizon)
    
    return {
        "risk_tolerance": risk_tolerance,
        "time_horizon": time_horizon,
        "optimized_allocation": optimized_allocation,
        "risk_score": calculate_risk_score(optimized_allocation)
    }

# 计算风险评分
def calculate_risk_score(allocation: Dict[str, float]) -> float:
    """根据资产配置计算风险评分"""
    risk_weights = {
        "cash": 1,
        "stocks": 10,
        "bonds": 3,
        "real_estate": 5,
        "commodities": 7,
        "alternative": 8
    }
    
    total_risk = 0
    total_weight = 0
    
    for asset_type, weight in allocation.items():
        if asset_type in risk_weights:
            total_risk += weight * risk_weights[asset_type]
            total_weight += weight
    
    return round(total_risk / total_weight, 2) if total_weight > 0 else 0

# 获取现金流分析
@router.get("/cash-flow-analysis")
async def get_cash_flow_analysis():
    """获取现金流分析结果"""
    init_mock_data()
    analysis_result = analyze_cash_flow(cash_flows)
    return analysis_result

# 添加新的现金流记录
@router.post("/cash-flows", response_model=CashFlow)
async def add_cash_flow(cash_flow: CashFlow):
    """添加新的现金流记录"""
    init_mock_data()
    
    new_id = len(cash_flows) + 1
    new_cash_flow = cash_flow.model_copy()
    new_cash_flow.id = new_id
    
    cash_flows.append(new_cash_flow)
    return new_cash_flow

# 更新投资计划
@router.post("/plans", response_model=InvestmentPlan)
async def add_investment_plan(plan: InvestmentPlan):
    """添加新的投资计划"""
    init_mock_data()
    
    new_id = len(investment_plans) + 1
    new_plan = plan.model_copy()
    new_plan.id = new_id
    
    # 计算下一次投资日期
    if new_plan.next_investment_date is None:
        if new_plan.frequency == "monthly":
            new_plan.next_investment_date = new_plan.start_date + timedelta(days=30)
        elif new_plan.frequency == "quarterly":
            new_plan.next_investment_date = new_plan.start_date + timedelta(days=90)
        elif new_plan.frequency == "yearly":
            new_plan.next_investment_date = new_plan.start_date.replace(year=new_plan.start_date.year + 1)
    
    investment_plans.append(new_plan)
    return new_plan
