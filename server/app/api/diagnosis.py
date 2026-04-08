from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.diagnosis import DiagnosisResult
from app.api.stocks import get_stock_kline, get_stock_realtime
from app.database import get_db
import numpy as np

router = APIRouter()

# 技术面分析
def analyze_technical(kline_data):
    if not kline_data or len(kline_data) < 20:
        return 50, []
    
    closes = [float(item['close']) for item in kline_data]
    
    # 计算移动平均线
    ma5 = np.mean(closes[-5:])
    ma20 = np.mean(closes[-20:])
    
    # 计算价格变化率
    price_change = (closes[-1] - closes[0]) / closes[0] * 100
    
    # 计算波动率
    volatility = np.std(closes) / np.mean(closes) * 100
    
    # 计算RSI
    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        if change > 0:
            gains.append(change)
        else:
            losses.append(abs(change))
    
    avg_gain = np.mean(gains) if gains else 0
    avg_loss = np.mean(losses) if losses else 0
    rsi = 100 - (100 / (1 + avg_gain/avg_loss)) if avg_loss > 0 else 50
    
    # 评分计算
    score = 50
    
    # 均线关系
    if ma5 > ma20:
        score += 15
    elif ma5 < ma20:
        score -= 15
    
    # 价格趋势
    if price_change > 10:
        score += 20
    elif price_change > 0:
        score += 10
    elif price_change < -10:
        score -= 20
    elif price_change < 0:
        score -= 10
    
    # RSI指标
    if 30 <= rsi <= 70:
        score += 10
    elif rsi > 70:
        score -= 10
    elif rsi < 30:
        score -= 10
    
    # 波动率
    if volatility < 3:
        score += 5
    elif volatility > 8:
        score -= 5
    
    # 分析结果
    factors = []
    if ma5 > ma20:
        factors.append("均线多头排列，趋势向好")
    else:
        factors.append("均线空头排列，趋势走弱")
    
    if price_change > 0:
        factors.append("近期价格上涨")
    else:
        factors.append("近期价格下跌")
    
    if 30 <= rsi <= 70:
        factors.append("RSI处于合理区间")
    elif rsi > 70:
        factors.append("RSI超买，可能回调")
    else:
        factors.append("RSI超卖，可能反弹")
    
    return max(0, min(100, score)), factors

# 基本面分析（基于简化的财务指标）
def analyze_fundamental(stock_code):
    # 这里使用简化的基本面分析，实际应该获取财务数据
    # 基于股票代码的行业特性进行评分
    industry_scores = {
        "600036": 85,  # 招商银行 - 金融
        "600519": 90,  # 贵州茅台 - 消费
        "000858": 85,  # 五粮液 - 消费
        "000333": 80,  # 美的集团 - 家电
        "601318": 75,  # 中国平安 - 金融
        "300750": 85,  # 宁德时代 - 新能源
        "002594": 85,  # 比亚迪 - 新能源
        "601398": 70   # 工商银行 - 金融
    }
    
    score = industry_scores.get(stock_code, 70)
    
    factors = []
    if score >= 85:
        factors.append("行业龙头，基本面优秀")
        factors.append("盈利能力强")
        factors.append("成长性良好")
    elif score >= 75:
        factors.append("行业地位稳固")
        factors.append("财务状况稳健")
    else:
        factors.append("行业竞争激烈")
        factors.append("增长潜力有限")
    
    return score, factors

# 市场面分析
def analyze_market(realtime_data):
    if not realtime_data:
        return 50, []
    
    price = realtime_data.get("price", 0)
    change = realtime_data.get("change", 0)
    change_percent = realtime_data.get("changePercent", 0)
    
    score = 50
    
    # 价格变动
    if change_percent > 5:
        score += 25
    elif change_percent > 0:
        score += 15
    elif change_percent < -5:
        score -= 25
    elif change_percent < 0:
        score -= 15
    
    # 交易量（如果有）
    volume = realtime_data.get("volume", 0)
    if volume > 1000000:
        score += 5
    elif volume < 100000:
        score -= 5
    
    factors = []
    if change_percent > 0:
        factors.append("市场表现活跃")
        if change_percent > 3:
            factors.append("资金流入明显")
    else:
        factors.append("市场表现疲软")
        if change_percent < -3:
            factors.append("资金流出迹象")
    
    return max(0, min(100, score)), factors

# 生成诊断结果
async def generate_diagnosis(stock_code: str, stock_name: str, db: Session) -> DiagnosisResult:
    try:
        # 获取K线数据进行技术面分析
        kline_data = await get_stock_kline(stock_code, interval="1d", days=60, db=db)
        technical_score, technical_factors = analyze_technical(kline_data["data"])
        
        # 获取实时数据进行市场面分析
        realtime_data = await get_stock_realtime(stock_code, db)
        market_score, market_factors = analyze_market(realtime_data)
        
        # 基本面分析
        fundamental_score, fundamental_factors = analyze_fundamental(stock_code)
        
        # 计算总评分
        overall_score = round((technical_score * 0.4 + fundamental_score * 0.3 + market_score * 0.3))
        
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
        strengths = []
        weaknesses = []
        
        # 基于技术面因素
        if "均线多头排列" in technical_factors:
            strengths.append("技术形态良好")
        else:
            weaknesses.append("技术形态走弱")
        
        if "近期价格上涨" in technical_factors:
            strengths.append("价格趋势向好")
        else:
            weaknesses.append("价格趋势走弱")
        
        # 基于基本面因素
        if "基本面优秀" in fundamental_factors:
            strengths.append("基本面稳健")
        else:
            weaknesses.append("基本面一般")
        
        # 基于市场面因素
        if "市场表现活跃" in market_factors:
            strengths.append("市场表现活跃")
        else:
            weaknesses.append("市场表现疲软")
        
        # 确保有足够的优势和劣势
        if len(strengths) < 3:
            strengths.extend([
                "行业前景看好",
                "盈利能力强",
                "估值合理"
            ][:3 - len(strengths)])
        
        if len(weaknesses) < 3:
            weaknesses.extend([
                "短期波动较大",
                "估值偏高",
                "行业竞争激烈"
            ][:3 - len(weaknesses)])
        
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
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation
        )
    except Exception as e:
        print(f"诊断分析失败: {e}")
        # 失败时返回基本的诊断结果
        return DiagnosisResult(
            stockCode=stock_code,
            stockName=stock_name,
            technicalScore=50,
            fundamentalScore=50,
            marketScore=50,
            overallScore=50,
            rating="neutral",
            strengths=["数据获取失败，无法进行全面分析"],
            weaknesses=["数据获取失败，无法进行全面分析"],
            recommendation="数据获取失败，请稍后再试。"
        )

# 获取股票诊断结果
@router.get("/{code}", response_model=DiagnosisResult)
async def get_diagnosis(code: str, db: Session = Depends(get_db)):
    # 股票名称映射
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
    
    try:
        diagnosis_result = await generate_diagnosis(code, stock_name, db)
        return diagnosis_result
    except Exception as e:
        print(f"诊断分析失败: {e}")
        # 失败时返回基本的诊断结果
        return DiagnosisResult(
            stockCode=code,
            stockName=stock_name,
            technicalScore=50,
            fundamentalScore=50,
            marketScore=50,
            overallScore=50,
            rating="neutral",
            strengths=["数据获取失败，无法进行全面分析"],
            weaknesses=["数据获取失败，无法进行全面分析"],
            recommendation="数据获取失败，请稍后再试。"
        )
