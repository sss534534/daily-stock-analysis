from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.analysis import (
    AIRecommendation, RiskAnalysis, RiskFactor,
    ChanTheoryAnalysis, ChanPivot, ChanBuyPoint, ChanSellPoint,
    LivermoreAnalysis, LivermorePivotalPoint
)
from app.database import get_db
from app.api.stocks import get_stock_kline
import random
from datetime import datetime, timedelta
from app.analysis.chan_theory import ChanTheoryAnalyzer

router = APIRouter()

# 生成AI推荐
def generate_ai_recommendation(stock_code: str, stock_name: str) -> AIRecommendation:
    types = ["buy", "sell", "hold"]
    timeframes = ["短期", "中期", "长期"]
    
    type = random.choice(types)
    confidence = round(random.uniform(70, 100), 2)
    timeframe = random.choice(timeframes)
    
    if type == "buy":
        reason = "技术形态向好，基本面稳健，市场资金流入明显，具备上涨潜力。"
        target_price = round(random.uniform(100, 120), 2)
        stop_loss = round(random.uniform(90, 95), 2)
    elif type == "sell":
        reason = "技术形态走弱，基本面存在不确定性，市场资金流出，建议及时止盈或止损。"
        target_price = None
        stop_loss = None
    else:
        reason = "当前市场走势不明朗，建议暂时观望，等待更清晰的信号。"
        target_price = None
        stop_loss = None
    
    return AIRecommendation(
        type=type,
        confidence=confidence,
        reason=reason,
        targetPrice=target_price,
        stopLoss=stop_loss,
        timeframe=timeframe
    )

# 生成风险分析
def generate_risk_analysis() -> RiskAnalysis:
    levels = ["low", "medium", "high", "extreme"]
    level = random.choice(levels)
    
    if level == "low":
        score = round(random.uniform(10, 30), 2)
    elif level == "medium":
        score = round(random.uniform(30, 50), 2)
    elif level == "high":
        score = round(random.uniform(50, 70), 2)
    else:
        score = round(random.uniform(70, 90), 2)
    
    factors = [
        RiskFactor(
            name="市场风险",
            impact=round(random.uniform(10, 40), 2),
            description="大盘波动可能对个股产生影响"
        ),
        RiskFactor(
            name="行业风险",
            impact=round(random.uniform(10, 40), 2),
            description="行业政策变化或竞争加剧"
        ),
        RiskFactor(
            name="公司风险",
            impact=round(random.uniform(10, 40), 2),
            description="公司业绩不及预期或内部管理问题"
        ),
        RiskFactor(
            name="流动性风险",
            impact=round(random.uniform(10, 40), 2),
            description="股票交易不活跃可能影响买卖"
        )
    ]
    
    return RiskAnalysis(
        level=level,
        score=score,
        factors=factors
    )

# 生成利弗莫尔分析
def generate_livermore_analysis() -> LivermoreAnalysis:
    market_phases = ["accumulation", "markup", "distribution", "markdown"]
    market_phase = random.choice(market_phases)
    
    # 生成关键点
    pivotal_points = []
    for i in range(random.randint(2, 4)):
        pivotal_points.append(LivermorePivotalPoint(
            price=round(random.uniform(80, 130), 2),
            type="阻力位" if i % 2 == 0 else "支撑位"
        ))
    
    trend_strength = round(random.uniform(30, 80), 2)
    
    # 生成量能分析
    volume_analysis = random.choice([
        "量价配合良好，上涨有成交量支持",
        "成交量萎缩，市场参与度降低",
        "量价背离，需谨慎对待",
        "放量突破，趋势可能反转"
    ])
    
    # 生成建议
    if market_phase == "accumulation":
        recommendation = "市场处于积累阶段，建议逢低布局，耐心等待上涨。"
    elif market_phase == "markup":
        recommendation = "市场处于上升阶段，建议持有或适量加仓，顺势而为。"
    elif market_phase == "distribution":
        recommendation = "市场处于派发阶段，建议逐步减仓，落袋为安。"
    else:
        recommendation = "市场处于下跌阶段，建议观望为主，避免抄底。"
    
    return LivermoreAnalysis(
        marketPhase=market_phase,
        pivotalPoints=pivotal_points,
        trendStrength=trend_strength,
        volumeAnalysis=volume_analysis,
        recommendation=recommendation
    )

# 获取AI分析
@router.get("/ai/{code}", response_model=AIRecommendation)
async def get_ai_analysis(code: str):
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
    
    ai_recommendation = generate_ai_recommendation(code, stock_name)
    return ai_recommendation

# 获取风险分析
@router.get("/risk/{code}", response_model=RiskAnalysis)
async def get_risk_analysis(code: str):
    risk_analysis = generate_risk_analysis()
    return risk_analysis

# 获取缠论分析
@router.get("/chan/{code}", response_model=ChanTheoryAnalysis)
async def get_chan_analysis(code: str, db: Session = Depends(get_db)):
    # 获取K线数据
    kline_data = await get_stock_kline(code, interval="1d", days=120, db=db)
    
    # 使用缠论分析器进行分析
    analyzer = ChanTheoryAnalyzer()
    analysis_result = analyzer.analyze(kline_data["data"])
    
    # 转换为响应模型
    pivots = [ChanPivot(
        type=p["type"],
        price=p["price"],
        date=p["date"]
    ) for p in analysis_result["pivots"]]
    
    buy_points = [ChanBuyPoint(
        price=b["price"],
        date=b["date"],
        confidence=b["confidence"]
    ) for b in analysis_result["buyPoints"]]
    
    sell_points = [ChanSellPoint(
        price=s["price"],
        date=s["date"],
        confidence=s["confidence"]
    ) for s in analysis_result["sellPoints"]]
    
    return ChanTheoryAnalysis(
        trend=analysis_result["trend"],
        level=1,  # 暂时设置为1级
        pivots=pivots,
        segments=analysis_result["segments"],
        buyPoints=buy_points,
        sellPoints=sell_points
    )

# 获取利弗莫尔分析
@router.get("/livermore/{code}", response_model=LivermoreAnalysis)
async def get_livermore_analysis(code: str):
    livermore_analysis = generate_livermore_analysis()
    return livermore_analysis

# 获取带缠论分析的K线数据
@router.get("/chan/kline/{code}")
async def get_chan_kline_analysis(code: str, interval: str = "1d", days: int = 120, db: Session = Depends(get_db)):
    # 获取K线数据
    kline_data = await get_stock_kline(code, interval=interval, days=days, db=db)
    
    # 使用缠论分析器进行分析
    analyzer = ChanTheoryAnalyzer()
    analysis_result = analyzer.analyze(kline_data["data"])
    
    # 整合K线数据和分析结果
    return {
        "code": kline_data["code"],
        "name": kline_data["name"],
        "interval": kline_data["interval"],
        "kline_data": kline_data["data"],
        "chan_analysis": analysis_result
    }

