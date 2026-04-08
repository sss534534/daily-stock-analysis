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
import math

router = APIRouter()

# 计算移动平均线
def calculate_ma(prices, period):
    if len(prices) < period:
        return []
    ma_values = []
    for i in range(period - 1, len(prices)):
        ma = sum(prices[i - period + 1:i + 1]) / period
        ma_values.append(ma)
    return ma_values

# 计算MACD
def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    if len(prices) < slow_period + signal_period:
        return None, None, None
    
    ema_fast = []
    ema_slow = []
    
    # 计算快速EMA
    k_fast = 2.0 / (fast_period + 1)
    ema_fast.append(prices[0])
    for price in prices[1:]:
        ema_fast.append((price - ema_fast[-1]) * k_fast + ema_fast[-1])
    
    # 计算慢速EMA
    k_slow = 2.0 / (slow_period + 1)
    ema_slow.append(prices[0])
    for price in prices[1:]:
        ema_slow.append((price - ema_slow[-1]) * k_slow + ema_slow[-1])
    
    # 计算MACD线
    macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
    
    # 计算信号线
    signal_line = []
    k_signal = 2.0 / (signal_period + 1)
    signal_line.append(macd_line[0])
    for macd in macd_line[1:]:
        signal_line.append((macd - signal_line[-1]) * k_signal + signal_line[-1])
    
    # 计算柱状图
    histogram = [macd_line[i] - signal_line[i] for i in range(len(macd_line))]
    
    return macd_line[-1], signal_line[-1], histogram[-1]

# 计算RSI
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    
    deltas = []
    for i in range(1, len(prices)):
        deltas.append(prices[i] - prices[i - 1])
    
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # 计算后续RSI值
    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

# 生成AI推荐
async def generate_ai_recommendation(stock_code: str, stock_name: str, db: Session) -> AIRecommendation:
    # 获取K线数据
    kline_data = await get_stock_kline(stock_code, interval="1d", days=60, db=db)
    prices = [item["close"] for item in kline_data["data"]]
    
    if len(prices) < 30:
        # 如果数据不足，返回谨慎推荐
        return AIRecommendation(
            type="hold",
            confidence=70.0,
            reason="数据不足，建议等待更多数据后再做决策。",
            targetPrice=None,
            stopLoss=None,
            timeframe="短期"
        )
    
    # 计算技术指标
    ma5 = calculate_ma(prices, 5)
    ma10 = calculate_ma(prices, 10)
    ma20 = calculate_ma(prices, 20)
    ma60 = calculate_ma(prices, 60)
    
    macd_line, signal_line, histogram = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    
    # 分析趋势
    trend_score = 0
    
    # 均线分析
    if len(ma5) > 0 and len(ma10) > 0 and len(ma20) > 0:
        if ma5[-1] > ma10[-1] and ma10[-1] > ma20[-1]:
            trend_score += 30
        elif ma5[-1] < ma10[-1] and ma10[-1] < ma20[-1]:
            trend_score -= 30
    
    # MACD分析
    if macd_line is not None and signal_line is not None:
        if macd_line > signal_line and histogram > 0:
            trend_score += 20
        elif macd_line < signal_line and histogram < 0:
            trend_score -= 20
    
    # RSI分析
    if rsi is not None:
        if rsi < 30:
            trend_score += 15  # 超卖，可能反弹
        elif rsi > 70:
            trend_score -= 15  # 超买，可能回调
    
    # 价格动量分析
    recent_change = (prices[-1] - prices[-5]) / prices[-5] * 100
    if recent_change > 5:
        trend_score += 10
    elif recent_change < -5:
        trend_score -= 10
    
    # 成交量分析
    volumes = [item["volume"] for item in kline_data["data"]]
    if len(volumes) >= 5:
        avg_volume = sum(volumes[-5:]) / 5
        if volumes[-1] > avg_volume * 1.5:
            if recent_change > 0:
                trend_score += 5  # 放量上涨
            else:
                trend_score -= 5  # 放量下跌
    
    # 确定推荐类型和置信度
    if trend_score >= 30:
        recommendation_type = "buy"
        confidence = min(95, 70 + trend_score * 0.5)
        timeframe = "短期"
        current_price = prices[-1]
        target_price = round(current_price * 1.15, 2)
        stop_loss = round(current_price * 0.95, 2)
        
        reasons = []
        if ma5[-1] > ma10[-1] and ma10[-1] > ma20[-1]:
            reasons.append("均线多头排列")
        if macd_line > signal_line and histogram > 0:
            reasons.append("MACD金叉")
        if rsi and rsi < 40:
            reasons.append("RSI处于低位")
        if recent_change > 0:
            reasons.append("价格动量强劲")
        
        reason = "技术指标显示强势，" + "、".join(reasons) + "，建议买入。"
        
    elif trend_score <= -30:
        recommendation_type = "sell"
        confidence = min(95, 70 - trend_score * 0.5)
        timeframe = "短期"
        target_price = None
        stop_loss = None
        
        reasons = []
        if ma5[-1] < ma10[-1] and ma10[-1] < ma20[-1]:
            reasons.append("均线空头排列")
        if macd_line < signal_line and histogram < 0:
            reasons.append("MACD死叉")
        if rsi and rsi > 60:
            reasons.append("RSI处于高位")
        if recent_change < 0:
            reasons.append("价格动量疲软")
        
        reason = "技术指标显示弱势，" + "、".join(reasons) + "，建议卖出。"
        
    else:
        recommendation_type = "hold"
        confidence = 75.0
        timeframe = "短期"
        target_price = None
        stop_loss = None
        reason = "当前市场走势不明朗，多空力量均衡，建议暂时观望。"
    
    return AIRecommendation(
        type=recommendation_type,
        confidence=round(confidence, 2),
        reason=reason,
        targetPrice=target_price,
        stopLoss=stop_loss,
        timeframe=timeframe
    )

# 计算波动率
def calculate_volatility(prices, period=20):
    if len(prices) < period:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    
    if len(returns) < period:
        return 0.0
    
    recent_returns = returns[-period:]
    avg_return = sum(recent_returns) / len(recent_returns)
    
    variance = sum((r - avg_return) ** 2 for r in recent_returns) / len(recent_returns)
    volatility = math.sqrt(variance) * math.sqrt(252)  # 年化波动率
    
    return volatility

# 计算最大回撤
def calculate_max_drawdown(prices):
    if len(prices) < 2:
        return 0.0
    
    max_drawdown = 0.0
    peak = prices[0]
    
    for price in prices[1:]:
        if price > peak:
            peak = price
        else:
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    
    return max_drawdown * 100  # 转换为百分比

# 计算贝塔系数（简化版）
def calculate_beta(stock_prices, market_prices):
    if len(stock_prices) < 2 or len(market_prices) < 2:
        return 1.0
    
    stock_returns = []
    market_returns = []
    
    for i in range(1, min(len(stock_prices), len(market_prices))):
        stock_returns.append((stock_prices[i] - stock_prices[i-1]) / stock_prices[i-1])
        market_returns.append((market_prices[i] - market_prices[i-1]) / market_prices[i-1])
    
    if len(stock_returns) < 10:
        return 1.0
    
    # 计算协方差和市场方差
    avg_stock_return = sum(stock_returns) / len(stock_returns)
    avg_market_return = sum(market_returns) / len(market_returns)
    
    covariance = sum((s - avg_stock_return) * (m - avg_market_return) 
                    for s, m in zip(stock_returns, market_returns)) / len(stock_returns)
    
    market_variance = sum((m - avg_market_return) ** 2 
                         for m in market_returns) / len(market_returns)
    
    if market_variance == 0:
        return 1.0
    
    beta = covariance / market_variance
    return beta

# 生成风险分析
async def generate_risk_analysis(stock_code: str, db: Session) -> RiskAnalysis:
    # 获取股票K线数据
    kline_data = await get_stock_kline(stock_code, interval="1d", days=60, db=db)
    prices = [item["close"] for item in kline_data["data"]]
    
    if len(prices) < 20:
        # 如果数据不足，返回中等风险
        return RiskAnalysis(
            level="medium",
            score=40.0,
            factors=[
                RiskFactor(
                    name="数据不足",
                    impact=30.0,
                    description="历史数据不足，风险评估准确性受限"
                ),
                RiskFactor(
                    name="市场风险",
                    impact=25.0,
                    description="市场整体波动风险"
                )
            ]
        )
    
    # 计算风险指标
    volatility = calculate_volatility(prices)
    max_drawdown = calculate_max_drawdown(prices)
    
    # 假设市场指数数据（简化处理）
    market_prices = [p * (0.98 + random.random() * 0.04) for p in prices]
    beta = calculate_beta(prices, market_prices)
    
    # 计算流动性风险
    volumes = [item["volume"] for item in kline_data["data"]]
    avg_volume = sum(volumes[-20:]) / len(volumes[-20:])
    liquidity_risk = 20.0 if avg_volume < 1000000 else 10.0
    
    # 计算风险评分
    risk_score = 0.0
    
    # 波动率风险 (30%)
    if volatility > 0.5:
        risk_score += volatility * 30
    elif volatility > 0.3:
        risk_score += volatility * 25
    else:
        risk_score += volatility * 20
    
    # 最大回撤风险 (25%)
    risk_score += max_drawdown * 0.25
    
    # 贝塔系数风险 (20%)
    if beta > 1.5:
        risk_score += (beta - 1) * 20
    elif beta < 0.5:
        risk_score += (1 - beta) * 10
    
    # 流动性风险 (15%)
    risk_score += liquidity_risk
    
    # 价格趋势风险 (10%)
    recent_change = (prices[-1] - prices[-10]) / prices[-10] * 100
    if abs(recent_change) > 15:
        risk_score += 10
    
    # 确定风险等级
    if risk_score < 30:
        level = "low"
    elif risk_score < 50:
        level = "medium"
    elif risk_score < 70:
        level = "high"
    else:
        level = "extreme"
    
    # 生成风险因素
    factors = []
    
    if volatility > 0.4:
        factors.append(RiskFactor(
            name="波动率风险",
            impact=round(volatility * 100, 2),
            description=f"近期波动率较高，价格波动剧烈，风险较大"
        ))
    
    if max_drawdown > 20:
        factors.append(RiskFactor(
            name="回撤风险",
            impact=round(max_drawdown, 2),
            description=f"最大回撤达到{max_drawdown:.1f}%，存在较大下跌风险"
        ))
    
    if beta > 1.3:
        factors.append(RiskFactor(
            name="市场敏感性",
            impact=round(beta * 15, 2),
            description=f"贝塔系数为{beta:.2f}，对市场波动敏感"
        ))
    elif beta < 0.7:
        factors.append(RiskFactor(
            name="市场敏感性",
            impact=round((1 - beta) * 10, 2),
            description=f"贝塔系数为{beta:.2f}，市场相关性较低"
        ))
    
    if avg_volume < 500000:
        factors.append(RiskFactor(
            name="流动性风险",
            impact=liquidity_risk,
            description="成交量较低，可能面临流动性不足问题"
        ))
    
    if abs(recent_change) > 10:
        factors.append(RiskFactor(
            name="价格波动风险",
            impact=round(abs(recent_change) * 0.5, 2),
            description=f"近期价格波动较大，变动幅度{recent_change:.1f}%"
        ))
    
    # 确保至少有一个风险因素
    if not factors:
        factors.append(RiskFactor(
            name="市场风险",
            impact=20.0,
            description="整体市场环境存在不确定性"
        ))
    
    return RiskAnalysis(
        level=level,
        score=round(min(risk_score, 95), 2),
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
async def get_ai_analysis(code: str, db: Session = Depends(get_db)):
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
    
    ai_recommendation = await generate_ai_recommendation(code, stock_name, db)
    return ai_recommendation

# 获取风险分析
@router.get("/risk/{code}", response_model=RiskAnalysis)
async def get_risk_analysis(code: str, db: Session = Depends(get_db)):
    risk_analysis = await generate_risk_analysis(code, db)
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

