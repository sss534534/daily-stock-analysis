#!/usr/bin/env python3
"""
股票分析系统后端API
使用Python内置模块实现的简单HTTP服务器
"""
import http.server
import socketserver
import json
import urllib.request
from datetime import datetime, timedelta
import random

PORT = 3006

# 股票数据缓存
stock_cache = {}
# 缓存过期时间（秒）
CACHE_EXPIRY = 300  # 5分钟

# 尝试导入akshare
try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
    print("akshare导入成功，可以使用akshare获取股票数据")
except ImportError:
    AK_SHARE_AVAILABLE = False
    print("akshare导入失败，将使用其他数据源获取股票数据")

# 股票列表
STOCK_LIST = [
    {"code": "600036", "name": "招商银行"},
    {"code": "600519", "name": "贵州茅台"},
    {"code": "000858", "name": "五粮液"},
    {"code": "000333", "name": "美的集团"},
    {"code": "601318", "name": "中国平安"},
    {"code": "600276", "name": "恒瑞医药"},
    {"code": "601888", "name": "中国中免"},
    {"code": "600887", "name": "伊利股份"},
    {"code": "601899", "name": "紫金矿业"},
    {"code": "601166", "name": "兴业银行"},
]

# 从缓存获取数据
def get_from_cache(key):
    if key in stock_cache:
        data, timestamp = stock_cache[key]
        if datetime.now().timestamp() - timestamp < CACHE_EXPIRY:
            return data
    return None

# 保存数据到缓存
def save_to_cache(key, data):
    stock_cache[key] = (data, datetime.now().timestamp())

# 生成模拟K线数据
def generate_mock_kline(code, days=120):
    data = []
    base_price = 30.0
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        open_price = base_price * (1 + random.uniform(-0.02, 0.02))
        high_price = open_price * (1 + random.uniform(0, 0.03))
        low_price = open_price * (1 - random.uniform(0, 0.03))
        close_price = open_price * (1 + random.uniform(-0.02, 0.02))
        volume = int(random.uniform(1000000, 5000000))
        
        data.append({
            "date": date,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
        
        base_price = close_price
    
    return data

# 从akshare获取K线数据
def get_kline_from_akshare(code, days=120):
    try:
        # 计算开始日期
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 获取股票K线数据
        df = ak.stock_zh_a_daily(
            symbol=code,
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        # 转换为前端需要的格式
        data = []
        for index, row in df.iterrows():
            data.append({
                "date": index.strftime("%Y-%m-%d"),
                "open": round(row["open"], 2),
                "high": round(row["high"], 2),
                "low": round(row["low"], 2),
                "close": round(row["close"], 2),
                "volume": int(row["volume"])
            })
        
        return data
    except Exception as e:
        print(f"akshare获取K线数据失败: {e}")
        return None

# 从新浪财经获取K线数据
def get_kline_from_sina(code, days=120):
    try:
        # 构建URL
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        url = f"https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&ma=no&datalen={days}"
        
        # 发送请求
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # 转换数据格式
        formatted_data = []
        for item in data:
            formatted_data.append({
                "date": item["day"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(item["volume"])
            })
        
        return formatted_data
    except Exception as e:
        print(f"新浪财经获取K线数据失败: {e}")
        return None

class StockAPIHandler(http.server.BaseHTTPRequestHandler):
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
        
        # 获取单个股票详情
        elif path.startswith('/api/stocks/') and '/history' not in path and '/kline' not in path and '/realtime' not in path:
            code = path.split('/')[-1]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                # 生成模拟数据
                current_price = round(30.0 * (1 + random.uniform(-0.05, 0.05)), 2)
                change = round(random.uniform(-2, 2), 2)
                change_percent = round(random.uniform(-5, 5), 2)
                
                response = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "price": current_price,
                    "change": change,
                    "changePercent": change_percent,
                    "high": round(current_price * (1 + random.uniform(0, 0.03)), 2),
                    "low": round(current_price * (1 - random.uniform(0, 0.03)), 2),
                    "open": round(current_price * (1 + random.uniform(-0.02, 0.02)), 2),
                    "prevClose": round(current_price * (1 - random.uniform(-0.02, 0.02)), 2),
                    "volume": int(random.uniform(1000000, 5000000)),
                    "amount": int(current_price * random.uniform(1000000, 5000000))
                }
            else:
                response = {"error": "Stock not found"}
        
        # 获取股票历史数据
        elif '/api/stocks/' in path and '/history' in path:
            parts = path.split('/')
            code = parts[-2]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                # 从缓存获取数据
                cache_key = f"{code}_history"
                cached_data = get_from_cache(cache_key)
                if cached_data:
                    response = cached_data
                else:
                    # 生成模拟数据
                    days = 30
                    if '?days=' in path:
                        days = int(path.split('?days=')[-1])
                    
                    data = []
                    base_price = 30.0
                    for i in range(days):
                        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
                        price = base_price * (1 + random.uniform(-0.02, 0.02))
                        data.append({
                            "date": date,
                            "price": round(price, 2)
                        })
                        base_price = price
                    
                    # 保存到缓存
                    save_to_cache(cache_key, data)
                    response = data
            else:
                response = {"error": "Stock not found"}
        
        # 获取股票K线数据
        elif '/api/stocks/' in path and '/kline' in path:
            parts = path.split('/')
            code = parts[-2]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                # 从缓存获取数据
                cache_key = f"{code}_kline"
                cached_data = get_from_cache(cache_key)
                if cached_data:
                    response = cached_data
                else:
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
                    
                    # 获取K线数据
                    kline_data = None
                    
                    # 优先使用akshare
                    if AK_SHARE_AVAILABLE:
                        kline_data = get_kline_from_akshare(code, days)
                    
                    # 如果akshare获取失败，使用新浪财经
                    if not kline_data:
                        kline_data = get_kline_from_sina(code, days)
                    
                    # 如果所有数据源都失败，使用模拟数据
                    if not kline_data:
                        kline_data = generate_mock_kline(code, days)
                    
                    response = {
                        "code": stock["code"],
                        "name": stock["name"],
                        "interval": interval,
                        "data": kline_data
                    }
                    
                    # 保存到缓存
                    save_to_cache(cache_key, response)
            else:
                response = {"error": "Stock not found"}
        
        # 获取股票实时数据
        elif '/api/stocks/' in path and '/realtime' in path:
            code = path.split('/')[-2]
            stock = next((s for s in STOCK_LIST if s["code"] == code), None)
            if stock:
                # 生成模拟数据
                current_price = round(30.0 * (1 + random.uniform(-0.05, 0.05)), 2)
                change = round(random.uniform(-2, 2), 2)
                change_percent = round(random.uniform(-5, 5), 2)
                
                response = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "price": current_price,
                    "change": change,
                    "changePercent": change_percent,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                },
                {
                    "id": "2",
                    "stockCode": "600519",
                    "stockName": "贵州茅台",
                    "shares": 100,
                    "buyPrice": 1800.0,
                    "currentPrice": 1850.0,
                    "profit": 5000,
                    "profitPercent": 2.78,
                    "buyDate": "2024-01-01"
                }
            ]
        
        # 其他未匹配的路径
        else:
            response = {"error": "Endpoint not found"}
        
        # 发送响应
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        # 路由处理逻辑
        path = self.path
        
        # 处理投资组合相关的POST请求
        if path == '/api/portfolio':
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # 生成模拟响应
            response = {
                "id": str(random.randint(1000, 9999)),
                "...": "..."
            }
        
        # 其他未匹配的路径
        else:
            response = {"error": "Endpoint not found"}
        
        # 发送响应
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # 设置CORS头
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), StockAPIHandler) as httpd:
            print(f"Stock Analysis Backend running at http://localhost:{PORT}")
            print("API Endpoints:")
            print("  GET /api/health - Health check")
            print("  GET /api/stocks - Get stock list")
            print("  GET /api/stocks/{code} - Get stock detail")
            print("  GET /api/stocks/{code}/history - Get stock history")
            print("  GET /api/stocks/{code}/kline?interval=1d&days=120 - Get stock K-line data")
            print("  GET /api/stocks/{code}/realtime - Get realtime stock price")
            print("  GET /api/portfolio - Get portfolio")
            print("  POST /api/portfolio - Add portfolio item")
            print("\nPress Ctrl+C to stop the server")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")
