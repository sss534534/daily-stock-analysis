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
