#!/usr/bin/env python3
"""
简单的股票分析系统后端API
使用Python内置模块实现的简单HTTP服务器
"""
import http.server
import socketserver
import json
from datetime import datetime, timedelta
import random
import math

# 添加分析算法的导入
try:
    from server.app.analysis.chan_theory import ChanTheoryAnalyzer
    CHAN_THEORY_AVAILABLE = True
except ImportError:
    CHAN_THEORY_AVAILABLE = False

PORT = 3006

# 股票列表
STOCK_LIST = [
    {"code": "600036", "name": "招商银行"},
    {"code": "600519", "name": "贵州茅台"},
    {"code": "000858", "name": "五粮液"},
    {"code": "000333", "name": "美的集团"},
    {"code": "601318", "name": "中国平安"},
]

# 生成模拟K线数据
def generate_mock_kline(code, days=120):
    data = []
    base_price = 30.0
    for i in range(days):
        date_obj = datetime.now() - timedelta(days=days-i)
        date = date_obj.strftime("%Y-%m-%d")
        timestamp = int(date_obj.timestamp() * 1000)  # 毫秒时间戳
        open_price = base_price * (1 + random.uniform(-0.02, 0.02))
        high_price = open_price * (1 + random.uniform(0, 0.03))
        low_price = open_price * (1 - random.uniform(0, 0.03))
        close_price = open_price * (1 + random.uniform(-0.02, 0.02))
        volume = int(random.uniform(1000000, 5000000))
        
        data.append({
            "timestamp": timestamp,
            "date": date,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
        
        base_price = close_price
    
    return data

# AI分析算法
def calculate_ma(prices, period):
    if len(prices) < period:
        return []
    ma_values = []
    for i in range(period - 1, len(prices)):
        ma = sum(prices[i - period + 1:i + 1]) / period
        ma_values.append(ma)
    return ma_values

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    if len(prices) < slow_period + signal_period:
        return None, None, None
    
    ema_fast = []
    ema_slow = []
    
    k_fast = 2.0 / (fast_period + 1)
    ema_fast.append(prices[0])
    for price in prices[1:]:
        ema_fast.append((price - ema_fast[-1]) * k_fast + ema_fast[-1])
    
    k_slow = 2.0 / (slow_period + 1)
    ema_slow.append(prices[0])
    for price in prices[1:]:
        ema_slow.append((price - ema_slow[-1]) * k_slow + ema_slow[-1])
    
    macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
    
    signal_line = []
    k_signal = 2.0 / (signal_period + 1)
    signal_line.append(macd_line[0])
    for macd in macd_line[1:]:
        signal_line.append((macd - signal_line[-1]) * k_signal + signal_line[-1])
    
    histogram = [macd_line[i] - signal_line[i] for i in range(len(macd_line))]
    
    return macd_line[-1], signal_line[-1], histogram[-1]

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
    
    for i in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
        
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

def generate_ai_recommendation(kline_data):
    prices = [item["close"] for item in kline_data]
    
    if len(prices) < 30:
        return {
            "type": "hold",
            "confidence": 70.0,
            "reason": "数据不足，建议等待更多数据后再做决策。",
            "targetPrice": None,
            "stopLoss": None,
            "timeframe": "短期"
        }
    
    ma5 = calculate_ma(prices, 5)
    ma10 = calculate_ma(prices, 10)
    ma20 = calculate_ma(prices, 20)
    macd_line, signal_line, histogram = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    
    trend_score = 0
    
    if len(ma5) > 0 and len(ma10) > 0 and len(ma20) > 0:
        if ma5[-1] > ma10[-1] and ma10[-1] > ma20[-1]:
            trend_score += 30
        elif ma5[-1] < ma10[-1] and ma10[-1] < ma20[-1]:
            trend_score -= 30
    
    if macd_line is not None and signal_line is not None:
        if macd_line > signal_line and histogram > 0:
            trend_score += 20
        elif macd_line < signal_line and histogram < 0:
            trend_score -= 20
    
    if rsi is not None:
        if rsi < 30:
            trend_score += 15
        elif rsi > 70:
            trend_score -= 15
    
    recent_change = (prices[-1] - prices[-5]) / prices[-5] * 100
    if recent_change > 5:
        trend_score += 10
    elif recent_change < -5:
        trend_score -= 10
    
    volumes = [item["volume"] for item in kline_data]
    if len(volumes) >= 5:
        avg_volume = sum(volumes[-5:]) / 5
        if volumes[-1] > avg_volume * 1.5:
            if recent_change > 0:
                trend_score += 5
            else:
                trend_score -= 5
    
    if trend_score >= 30:
        recommendation_type = "buy"
        confidence = min(95, 70 + trend_score * 0.5)
        timeframe = "短期"
        current_price = prices[-1]
        target_price = round(current_price * 1.15, 2)
        stop_loss = round(current_price * 0.95, 2)
        
        reasons = []
        if len(ma5) > 0 and len(ma10) > 0 and len(ma20) > 0:
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
        if len(ma5) > 0 and len(ma10) > 0 and len(ma20) > 0:
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
    
    return {
        "type": recommendation_type,
        "confidence": round(confidence, 2),
        "reason": reason,
        "targetPrice": target_price,
        "stopLoss": stop_loss,
        "timeframe": timeframe
    }

# 风险分析算法
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
    volatility = math.sqrt(variance) * math.sqrt(252)
    
    return volatility

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
    
    return max_drawdown * 100

def generate_risk_analysis(kline_data):
    prices = [item["close"] for item in kline_data]
    
    if len(prices) < 20:
        return {
            "level": "medium",
            "score": 40.0,
            "factors": [
                {
                    "name": "数据不足",
                    "impact": 30.0,
                    "description": "历史数据不足，风险评估准确性受限"
                },
                {
                    "name": "市场风险",
                    "impact": 25.0,
                    "description": "市场整体波动风险"
                }
            ]
        }
    
    volatility = calculate_volatility(prices)
    max_drawdown = calculate_max_drawdown(prices)
    
    market_prices = [p * (0.98 + random.random() * 0.04) for p in prices]
    
    stock_returns = []
    market_returns = []
    for i in range(1, min(len(prices), len(market_prices))):
        stock_returns.append((prices[i] - prices[i-1]) / prices[i-1])
        market_returns.append((market_prices[i] - market_prices[i-1]) / market_prices[i-1])
    
    beta = 1.0
    if len(stock_returns) >= 10:
        avg_stock_return = sum(stock_returns) / len(stock_returns)
        avg_market_return = sum(market_returns) / len(market_returns)
        
        covariance = sum((s - avg_stock_return) * (m - avg_market_return) 
                        for s, m in zip(stock_returns, market_returns)) / len(stock_returns)
        
        market_variance = sum((m - avg_market_return) ** 2 
                             for m in market_returns) / len(market_returns)
        
        if market_variance > 0:
            beta = covariance / market_variance
    
    volumes = [item["volume"] for item in kline_data]
    avg_volume = sum(volumes[-20:]) / len(volumes[-20:])
    liquidity_risk = 20.0 if avg_volume < 1000000 else 10.0
    
    risk_score = 0.0
    
    if volatility > 0.5:
        risk_score += volatility * 30
    elif volatility > 0.3:
        risk_score += volatility * 25
    else:
        risk_score += volatility * 20
    
    risk_score += max_drawdown * 0.25
    
    if beta > 1.5:
        risk_score += (beta - 1) * 20
    elif beta < 0.5:
        risk_score += (1 - beta) * 10
    
    risk_score += liquidity_risk
    
    recent_change = (prices[-1] - prices[-10]) / prices[-10] * 100
    if abs(recent_change) > 15:
        risk_score += 10
    
    if risk_score < 30:
        level = "low"
    elif risk_score < 50:
        level = "medium"
    elif risk_score < 70:
        level = "high"
    else:
        level = "extreme"
    
    factors = []
    
    if volatility > 0.4:
        factors.append({
            "name": "波动率风险",
            "impact": round(volatility * 100, 2),
            "description": f"近期波动率较高，价格波动剧烈，风险较大"
        })
    
    if max_drawdown > 20:
        factors.append({
            "name": "回撤风险",
            "impact": round(max_drawdown, 2),
            "description": f"最大回撤达到{max_drawdown:.1f}%，存在较大下跌风险"
        })
    
    if beta > 1.3:
        factors.append({
            "name": "市场敏感性",
            "impact": round(beta * 15, 2),
            "description": f"贝塔系数为{beta:.2f}，对市场波动敏感"
        })
    elif beta < 0.7:
        factors.append({
            "name": "市场敏感性",
            "impact": round((1 - beta) * 10, 2),
            "description": f"贝塔系数为{beta:.2f}，市场相关性较低"
        })
    
    if avg_volume < 500000:
        factors.append({
            "name": "流动性风险",
            "impact": liquidity_risk,
            "description": "成交量较低，可能面临流动性不足问题"
        })
    
    if abs(recent_change) > 10:
        factors.append({
            "name": "价格波动风险",
            "impact": round(abs(recent_change) * 0.5, 2),
            "description": f"近期价格波动较大，变动幅度{recent_change:.1f}%"
        })
    
    if not factors:
        factors.append({
            "name": "市场风险",
            "impact": 20.0,
            "description": "整体市场环境存在不确定性"
        })
    
    return {
        "level": level,
        "score": round(min(risk_score, 95), 2),
        "factors": factors
    }

# 缠论分析（简化版）
def generate_chan_analysis(kline_data):
    if not CHAN_THEORY_AVAILABLE:
        return {
            "trend": "sideways",
            "level": 1,
            "pivots": [],
            "segments": ["缠论分析器不可用，返回模拟数据"],
            "buyPoints": [],
            "sellPoints": []
        }
    
    try:
        analyzer = ChanTheoryAnalyzer()
        analysis_result = analyzer.analyze(kline_data)
        return analysis_result
    except Exception as e:
        return {
            "trend": "sideways",
            "level": 1,
            "pivots": [],
            "segments": [f"缠论分析出错: {str(e)}"],
            "buyPoints": [],
            "sellPoints": []
        }

class SimpleStockAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        # 路由处理逻辑
        path = self.path
        
        # 健康检查
        if path == '/api/health':
            response = {
                "status": "ok",
                "message": "Stock Analysis Backend is running"
            }
        
        # 获取股票列表
        elif path == '/api/stocks':
            response = STOCK_LIST
        
        # 获取股票K线数据
        elif '/api/stocks/' in path and '/kline' in path:
            parts = path.split('/')
            code = parts[-2]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                # 解析参数
                interval = "1d"
                days = 120
                if '?interval=' in path:
                    params = path.split('?')[1].split('&')
                    for param in params:
                        if param.startswith('interval='):
                            interval = param.split('=')[1]
                        elif param.startswith('days='):
                            days = int(param.split('=')[1])
                
                # 生成模拟K线数据
                kline_data = generate_mock_kline(code, days)
                
                response = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "interval": interval,
                    "data": kline_data
                }
            else:
                response = {"error": "Stock not found"}
        
        # 获取投资组合数据
        elif path == '/api/portfolio':
            # 生成模拟数据
            response = [
                {
                    "id": "1",
                    "stockCode": "600036",
                    "stockName": "招商银行",
                    "shares": 1000,
                    "buyPrice": 30.0,
                    "currentPrice": 31.5,
                    "profit": 1500,
                    "profitPercent": 5.0,
                    "buyDate": "2024-01-01"
                }
            ]
        
        # AI分析API
        elif '/api/analysis/ai/' in path:
            code = path.split('/')[-1]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                kline_data = generate_mock_kline(code, 60)
                response = generate_ai_recommendation(kline_data)
            else:
                response = {"error": "Stock not found"}
        
        # 风险分析API
        elif '/api/analysis/risk/' in path:
            code = path.split('/')[-1]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                kline_data = generate_mock_kline(code, 60)
                response = generate_risk_analysis(kline_data)
            else:
                response = {"error": "Stock not found"}
        
        # 缠论分析API
        elif '/api/analysis/chan/' in path:
            code = path.split('/')[-1]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                kline_data = generate_mock_kline(code, 120)
                response = generate_chan_analysis(kline_data)
            else:
                response = {"error": "Stock not found"}
        
        # 带缠论分析的K线数据
        elif '/api/analysis/chan/kline/' in path:
            parts = path.split('/')
            code = parts[-2]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                interval = "1d"
                days = 120
                if '?interval=' in path:
                    params = path.split('?')[1].split('&')
                    for param in params:
                        if param.startswith('interval='):
                            interval = param.split('=')[1]
                        elif param.startswith('days='):
                            days = int(param.split('=')[1])
                
                kline_data = generate_mock_kline(code, days)
                try:
                    chan_analysis = generate_chan_analysis(kline_data)
                except Exception as e:
                    chan_analysis = {
                        "trend": "sideways",
                        "level": 1,
                        "pivots": [],
                        "segments": [f"缠论分析出错: {str(e)}"],
                        "buyPoints": [],
                        "sellPoints": []
                    }
                
                response = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "interval": interval,
                    "kline_data": kline_data,
                    "chan_analysis": chan_analysis
                }
            else:
                response = {"error": "Stock not found"}
        
        # 其他未匹配的路径
        else:
            response = {"error": "Endpoint not found"}
        
        # 发送响应
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # 设置CORS头
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == "__main__":
    print(f"Starting simple backend server on port {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), SimpleStockAPIHandler) as httpd:
            print(f"Simple Stock Analysis Backend running at http://localhost:{PORT}")
            print("API Endpoints:")
            print("  GET /api/health - Health check")
            print("  GET /api/stocks - Get stock list")
            print("  GET /api/stocks/{code}/kline?interval=1d&days=120 - Get stock K-line data")
            print("  GET /api/portfolio - Get portfolio")
            print("\nPress Ctrl+C to stop the server")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")
