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
import time

# 导入配置和工具模块
try:
    from config.datasources import (
        DATA_SOURCE_PRIORITY, DATA_SOURCE_CONFIG, 
        API_ENDPOINTS, STOCK_CODE_MAPPING, CACHE_CONFIG
    )
    from config.logging import logger
    from utils.retry import RetryManager
    from utils.data_validator import DataValidator
    CONFIG_LOADED = True
except ImportError as e:
    print(f"导入配置模块失败: {e}")
    CONFIG_LOADED = False

PORT = 3006

# 股票数据缓存
stock_cache = {}
# 缓存过期时间（秒）
CACHE_EXPIRY = CACHE_CONFIG.get("kline", {}).get("expiry", 300) if CONFIG_LOADED else 300

# 尝试导入akshare
try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
    print("akshare导入成功，可以使用akshare获取股票数据")
except ImportError:
    AK_SHARE_AVAILABLE = False
    print("akshare导入失败，将使用其他数据源获取股票数据")

# 数据源可用性状态
DATA_SOURCE_STATUS = {
    "akshare": AK_SHARE_AVAILABLE,
    "eastmoney": True,
    "tencent": True,
    "sina": True,
    "mock": True
}

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

# 从东方财富获取K线数据
def get_kline_from_eastmoney(code, days=120):
    """从东方财富获取K线数据"""
    try:
        # 根据股票代码确定市场前缀
        if code.startswith('6'):
            market = "1."  # 沪市
        else:
            market = "0."  # 深市和创业板
        
        # 构建URL
        url = f"{API_ENDPOINTS['eastmoney']['kline']}?secid={market}{code}&klt=101&fqt=1&beg=0&end=20500101"
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 创建请求对象
        req = urllib.request.Request(url, headers=headers)
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # 解析数据
        if data.get("data") and data["data"].get("klines"):
            formatted_data = []
            for kline in data["data"]["klines"]:
                parts = kline.split(',')
                if len(parts) >= 7:
                    formatted_data.append({
                        "date": parts[0],
                        "open": float(parts[1]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "close": float(parts[2]),
                        "volume": int(parts[5])
                    })
            
            # 限制返回的数据量
            if len(formatted_data) > days:
                formatted_data = formatted_data[-days:]
            
            # 验证数据
            if CONFIG_LOADED and not DataValidator.validate_kline_data(formatted_data):
                print("东方财富数据验证失败")
                return None
            
            return formatted_data
        
        return None
    except Exception as e:
        print(f"东方财富获取K线数据失败: {e}")
        return None

# 从腾讯财经获取K线数据
def get_kline_from_tencent(code, days=120):
    """从腾讯财经获取K线数据"""
    try:
        # 根据股票代码确定市场前缀
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        # 构建URL
        url = API_ENDPOINTS['tencent']['kline'].format(symbol=symbol, days=days)
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 创建请求对象
        req = urllib.request.Request(url, headers=headers)
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # 解析数据
        if data.get("data") and data["data"].get(symbol):
            kline_data = data["data"][symbol].get("day")
            if kline_data:
                formatted_data = []
                for item in kline_data:
                    formatted_data.append({
                        "date": item[0],
                        "open": float(item[1]),
                        "high": float(item[3]),
                        "low": float(item[4]),
                        "close": float(item[2]),
                        "volume": int(item[5])
                    })
                
                # 验证数据
                if CONFIG_LOADED and not DataValidator.validate_kline_data(formatted_data):
                    print("腾讯财经数据验证失败")
                    return None
                
                return formatted_data
        
        return None
    except Exception as e:
        print(f"腾讯财经获取K线数据失败: {e}")
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
        
        # 设置请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 创建请求对象
        req = urllib.request.Request(url, headers=headers)
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=8) as response:
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
        
        # 验证数据
        if CONFIG_LOADED and not DataValidator.validate_kline_data(formatted_data):
            print("新浪财经数据验证失败")
            return None
        
        return formatted_data
    except Exception as e:
        print(f"新浪财经获取K线数据失败: {e}")
        return None

# 获取K线数据（支持多数据源）
def get_kline_data(code, days=120):
    """从多个数据源获取K线数据，自动切换失败的数据源"""
    data_sources = []
    
    # 根据优先级尝试不同的数据源
    for source_name in DATA_SOURCE_PRIORITY:
        if not DATA_SOURCE_STATUS.get(source_name):
            continue
        
        try:
            if source_name == "akshare" and AK_SHARE_AVAILABLE:
                kline_data = get_kline_from_akshare(code, days)
            elif source_name == "eastmoney":
                kline_data = get_kline_from_eastmoney(code, days)
            elif source_name == "tencent":
                kline_data = get_kline_from_tencent(code, days)
            elif source_name == "sina":
                kline_data = get_kline_from_sina(code, days)
            elif source_name == "mock":
                kline_data = generate_mock_kline(code, days)
            else:
                continue
            
            if kline_data and len(kline_data) > 0:
                data_sources.append((source_name, kline_data))
                
                # 如果获取到足够的数据，直接返回
                if len(kline_data) >= days * 0.8:  # 至少获取80%的数据
                    print(f"成功从{source_name}获取K线数据")
                    return kline_data
                    
        except Exception as e:
            print(f"从{source_name}获取数据失败: {e}")
            DATA_SOURCE_STATUS[source_name] = False
    
    # 如果有多个数据源的数据，选择数据质量最好的
    if data_sources:
        # 按数据量排序
        data_sources.sort(key=lambda x: len(x[1]), reverse=True)
        print(f"从{data_sources[0][0]}获取到最多数据")
        return data_sources[0][1]
    
    # 所有数据源都失败，使用模拟数据
    print("所有数据源都失败，使用模拟数据")
    return generate_mock_kline(code, days)

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
                    
                    # 获取K线数据（使用多数据源自动切换机制）
                    try:
                        kline_data = get_kline_data(code, days)
                        print(f"成功获取{code}的K线数据，共{len(kline_data)}条记录")
                    except Exception as e:
                        print(f"获取K线数据失败: {e}")
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
                    "cost": 30000,
                    "totalValue": 31500,
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
                    "cost": 180000,
                    "totalValue": 185000,
                    "buyDate": "2024-01-01"
                }
            ]
        
        # 获取投资组合统计信息
        elif path == '/api/portfolio/stats':
            portfolio = [
                {"cost": 30000, "totalValue": 31500, "profit": 1500},
                {"cost": 180000, "totalValue": 185000, "profit": 5000}
            ]
            total_cost = sum(item["cost"] for item in portfolio)
            total_value = sum(item["totalValue"] for item in portfolio)
            total_profit = sum(item["profit"] for item in portfolio)
            total_profit_percent = round((total_profit / total_cost) * 100, 2) if total_cost > 0 else 0
            
            response = {
                "totalCost": total_cost,
                "totalValue": total_value,
                "totalProfit": total_profit,
                "totalProfitPercent": total_profit_percent,
                "positionCount": len(portfolio)
            }
        
        # 获取军规数据
        elif path == '/api/military-rules':
            response = {
                "rules": [
                    {
                        "id": 1,
                        "title": "军规 1",
                        "content": "莫求暴富，为自己设定一个长期目标",
                        "category": "目标设定",
                        "description": "投资是一场马拉松，不是短跑。设定合理的长期目标，避免追求短期暴富的心态。"
                    },
                    {
                        "id": 2,
                        "title": "军规 2",
                        "content": "永不满仓，找到自己的资产配置中枢",
                        "category": "资金管理",
                        "description": "保持合理的仓位，永远不要满仓操作，建立适合自己风险承受能力的资产配置方案。"
                    },
                    {
                        "id": 3,
                        "title": "军规 3",
                        "content": "均衡为王，构建基金经理1/2水平的投资组合",
                        "category": "投资组合",
                        "description": "diversification is the only free lunch in investing. 构建均衡的投资组合，降低单一资产风险。"
                    },
                    {
                        "id": 4,
                        "title": "军规 4",
                        "content": "定期复盘，优胜劣汰再平衡",
                        "category": "投资管理",
                        "description": "定期回顾投资表现，淘汰表现不佳的资产，重新平衡投资组合。"
                    },
                    {
                        "id": 5,
                        "title": "军规 5",
                        "content": "稳定心态，克服贪婪与恐惧",
                        "category": "心态管理",
                        "description": "在市场上涨时避免贪婪，在市场下跌时避免恐惧，保持理性的投资心态。"
                    },
                    {
                        "id": 6,
                        "title": "军规 6",
                        "content": "定期投入，必要时加倍",
                        "category": "投资策略",
                        "description": "采用定期投资策略，在市场低迷时可以适当增加投入，降低平均成本。"
                    },
                    {
                        "id": 7,
                        "title": "军规 7",
                        "content": "做好主业，保持现金流",
                        "category": "基础保障",
                        "description": "投资不是生活的全部，做好自己的主业，保持稳定的现金流，为投资提供持续的资金支持。"
                    }
                ],
                "total": 7
            }
        
        # 获取单个军规
        elif path.startswith('/api/military-rules/'):
            rule_id = int(path.split('/')[-1])
            rules = [
                {
                    "id": 1,
                    "title": "军规 1",
                    "content": "莫求暴富，为自己设定一个长期目标",
                    "category": "目标设定",
                    "description": "投资是一场马拉松，不是短跑。设定合理的长期目标，避免追求短期暴富的心态。"
                },
                {
                    "id": 2,
                    "title": "军规 2",
                    "content": "永不满仓，找到自己的资产配置中枢",
                    "category": "资金管理",
                    "description": "保持合理的仓位，永远不要满仓操作，建立适合自己风险承受能力的资产配置方案。"
                },
                {
                    "id": 3,
                    "title": "军规 3",
                    "content": "均衡为王，构建基金经理1/2水平的投资组合",
                    "category": "投资组合",
                    "description": "diversification is the only free lunch in investing. 构建均衡的投资组合，降低单一资产风险。"
                },
                {
                    "id": 4,
                    "title": "军规 4",
                    "content": "定期复盘，优胜劣汰再平衡",
                    "category": "投资管理",
                    "description": "定期回顾投资表现，淘汰表现不佳的资产，重新平衡投资组合。"
                },
                {
                    "id": 5,
                    "title": "军规 5",
                    "content": "稳定心态，克服贪婪与恐惧",
                    "category": "心态管理",
                    "description": "在市场上涨时避免贪婪，在市场下跌时避免恐惧，保持理性的投资心态。"
                },
                {
                    "id": 6,
                    "title": "军规 6",
                    "content": "定期投入，必要时加倍",
                    "category": "投资策略",
                    "description": "采用定期投资策略，在市场低迷时可以适当增加投入，降低平均成本。"
                },
                {
                    "id": 7,
                    "title": "军规 7",
                    "content": "做好主业，保持现金流",
                    "category": "基础保障",
                    "description": "投资不是生活的全部，做好自己的主业，保持稳定的现金流，为投资提供持续的资金支持。"
                }
            ]
            for rule in rules:
                if rule["id"] == rule_id:
                    response = rule
                    break
            else:
                response = rules[0]
        
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
