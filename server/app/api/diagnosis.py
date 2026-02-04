from fastapi import APIRouter, HTTPException
from app.models.diagnosis import DiagnosisResult
import random

router = APIRouter()

# 模拟股票诊断数据
def generate_diagnosis(stock_code: str, stock_name: str) -> DiagnosisResult:
    # 随机生成评分
    technical_score = random.randint(70, 100)
    fundamental_score = random.randint(70, 100)
    market_score = random.randint(70, 100)
    overall_score = (technical_score + fundamental_score + market_score) // 3
    
    # 根据总评分确定评级
    if overall_score >= 90:
        rating = "excellent"
    elif overall_score >= 80:
        rating = "good"
    elif overall_score >= 70:
        rating = "neutral"
    elif overall_score >= 60:
        rating = "poor"
    else:
        rating = "risk"
    
    # 生成优势和劣势
    strengths = [
        "技术形态良好",
        "基本面稳健",
        "市场表现活跃",
        "资金流入明显",
        "行业前景看好",
        "盈利能力强",
        "成长性佳",
        "估值合理"
    ]
    
    weaknesses = [
        "短期波动较大",
        "估值偏高",
        "行业竞争激烈",
        "业绩增长放缓",
        "资金流出迹象",
        "技术指标超买",
        "市场情绪谨慎",
        "外部风险因素"
    ]
    
    # 随机选择3-5个优势和劣势
    selected_strengths = []
    selected_weaknesses = []
    
    for _ in range(random.randint(3, 5)):
        strength = random.choice(strengths)
        if strength not in selected_strengths:
            selected_strengths.append(strength)
    
    for _ in range(random.randint(3, 5)):
        weakness = random.choice(weaknesses)
        if weakness not in selected_weaknesses:
            selected_weaknesses.append(weakness)
    
    # 生成建议
    if rating == "excellent":
        recommendation = "强烈推荐买入，具有良好的投资价值和上涨空间。"
    elif rating == "good":
        recommendation = "推荐买入，具备一定的投资价值和上涨潜力。"
    elif rating == "neutral":
        recommendation = "建议持有，暂时观望市场走势。"
    elif rating == "poor":
        recommendation = "建议谨慎持有，考虑减仓或止损。"
    else:
        recommendation = "强烈建议卖出，存在较大的下跌风险。"
    
    return DiagnosisResult(
        stockCode=stock_code,
        stockName=stock_name,
        technicalScore=technical_score,
        fundamentalScore=fundamental_score,
        marketScore=market_score,
        overallScore=overall_score,
        rating=rating,
        strengths=selected_strengths,
        weaknesses=selected_weaknesses,
        recommendation=recommendation
    )

# 获取股票诊断结果
@router.get("/{code}", response_model=DiagnosisResult)
async def get_diagnosis(code: str):
    # 模拟股票名称
    stock_names = {
        "600036": "招商银行",
        "600519": "贵州茅台",
        "000858": "五粮液",
        "000333": "美的集团",
        "601318": "中国平安",
        "300750": "宁德时代",
        "002594": "比亚迪",
        "601398": "工商银行"
    }
    
    stock_name = stock_names.get(code, "未知股票")
    diagnosis_result = generate_diagnosis(code, stock_name)
    
    return diagnosis_result
