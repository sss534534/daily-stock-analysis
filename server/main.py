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

PORT = 3004

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
    {"code": "300750", "name": "宁德时代"},
    {"code": "002594", "name": "比亚迪"},
    {"code": "601398", "name": "工商银行"}
]

class StockAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        # 解析路径
        path = self.path
        
        # 健康检查
        if path == '/api/health':
            response = {"status": "ok", "message": "Stock Analysis Backend is running"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取股票列表
        elif path == '/api/stocks':
            response = self.get_stock_list()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取单个股票详情
        elif path.startswith('/api/stocks/') and not path.endswith('/history') and not path.endswith('/kline') and not path.endswith('/realtime'):
            code = path.split('/')[-1]
            response = self.get_stock_detail(code)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取股票历史数据
        elif path.endswith('/history'):
            code = path.split('/')[-2]
            response = self.get_stock_history(code)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取股票K线数据
        elif path.endswith('/kline'):
            code = path.split('/')[-2]
            # 解析查询参数
            import urllib.parse
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            interval = params.get('interval', ['1d'])[0]
            days = int(params.get('days', ['120'])[0])
            response = self.get_stock_kline(code, interval, days)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取实时股票价格
        elif path.endswith('/realtime'):
            code = path.split('/')[-2]
            response = self.get_stock_realtime(code)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 获取缠论分析
        elif path.startswith('/api/analysis/chan/kline/'):
            code = path.split('/')[-1]
            # 解析查询参数
            import urllib.parse
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            interval = params.get('interval', ['1d'])[0]
            days = int(params.get('days', ['120'])[0])
            response = self.get_chan_kline_analysis(code, interval, days)
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        # 其他API路径返回模拟数据
        else:
            response = {"message": "API endpoint not found"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
    
    def get_stock_list(self):
        """获取股票列表"""
        stocks = []
        for stock in STOCK_LIST:
            # 生成模拟数据
            base_price = random.uniform(5, 2000)
            change = random.uniform(-10, 10)
            change_percent = (change / base_price) * 100
            
            stocks.append({
                "id": stock["code"],
                "code": stock["code"],
                "name": stock["name"],
                "price": round(base_price + change, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2),
                "volume": random.randint(1000000, 100000000),
                "marketCap": random.randint(10000000000, 3000000000000)
            })
        return stocks
    
    def get_stock_detail(self, code):
        """获取单个股票详情"""
        stock = next((s for s in STOCK_LIST if s["code"] == code), None)
        if not stock:
            return {"error": "Stock not found"}
        
        # 生成模拟数据
        base_price = random.uniform(5, 2000)
        change = random.uniform(-10, 10)
        change_percent = (change / base_price) * 100
        
        return {
            "id": code,
            "code": code,
            "name": stock["name"],
            "price": round(base_price + change, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "volume": random.randint(1000000, 100000000),
            "marketCap": random.randint(10000000000, 3000000000000)
        }
    
    def get_stock_history(self, code):
        """获取股票历史数据"""
        stock = next((s for s in STOCK_LIST if s["code"] == code), None)
        if not stock:
            return []
        
        # 生成模拟历史数据
        history = []
        base_price = random.uniform(5, 2000)
        end_date = datetime.now()
        
        for i in range(30):
            date = end_date - timedelta(days=30-i)
            change = (random.random() - 0.48) * (base_price * 0.03)
            base_price = max(base_price + change, 1)
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(base_price, 2),
                "volume": random.randint(1000000, 10000000),
                "high": round(base_price * 1.02, 2),
                "low": round(base_price * 0.98, 2),
                "open": round(base_price * (0.98 + random.random() * 0.04), 2)
            })
        
        return history
    
    def get_stock_kline(self, code, interval, days):
        """获取股票K线数据"""
        stock = next((s for s in STOCK_LIST if s["code"] == code), None)
        if not stock:
            return {"error": "Stock not found"}
        
        # 生成缓存键
        cache_key = f"kline:{code}:{interval}:{days}"
        current_time = datetime.now().timestamp()
        
        # 检查缓存是否有效
        if cache_key in stock_cache:
            cached_data = stock_cache[cache_key]
            if current_time - cached_data["timestamp"] < CACHE_EXPIRY:
                print(f"Using cached K-line data for {code}")
                return cached_data["data"]
        
        # 尝试使用akshare获取数据
        if AK_SHARE_AVAILABLE:
            try:
                print(f"Using akshare to fetch K-line data for {code}")
                # 计算日期范围
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # 使用akshare获取K线数据
                # 注意：akshare的stock_zh_a_daily函数需要的是股票代码，不需要市场后缀
                df = ak.stock_zh_a_daily(
                    symbol=code,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    adjust="qfq"  # 使用前复权数据
                )
                
                # 转换数据格式
                formatted_data = []
                for index, row in df.iterrows():
                    date_str = index.strftime("%Y-%m-%d")
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_data.append({
                        "timestamp": int(date.timestamp() * 1000),
                        "date": date_str,
                        "open": float(row['open']),
                        "high": float(row['high']),
                        "low": float(row['low']),
                        "close": float(row['close']),
                        "volume": int(row['volume'])
                    })
                
                # 按日期排序（从早到晚）
                formatted_data.sort(key=lambda x: x['timestamp'])
                
                result = {
                    "code": code,
                    "name": stock["name"],
                    "interval": interval,
                    "data": formatted_data
                }
                
                # 缓存数据
                stock_cache[cache_key] = {
                    "timestamp": current_time,
                    "data": result
                }
                
                return result
            except Exception as e:
                print(f"Error fetching data with akshare: {e}")
                # 继续尝试其他数据源
        
        # 尝试从外部API获取真实数据
        try:
            # 使用新浪财经API获取股票数据
            if code.startswith('6'):
                symbol = f'sh{code}'  # 沪市
            else:
                symbol = f'sz{code}'  # 深市
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 调用新浪财经API
            url = f'http://quotes.sina.cn/cn/api/jsonp.php/var%20_{symbol}=/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&datalen={days}'
            import urllib.request
            response = urllib.request.urlopen(url, timeout=5)
            data = response.read().decode('utf-8')
            
            # 解析数据
            import re
            json_data = re.search(r'\((.*)\)', data).group(1)
            kline_data = json.loads(json_data)
            
            # 转换数据格式
            formatted_data = []
            for item in kline_data:
                date = datetime.strptime(item['day'], '%Y-%m-%d')
                formatted_data.append({
                    "timestamp": int(date.timestamp() * 1000),
                    "date": item['day'],
                    "open": float(item['open']),
                    "high": float(item['high']),
                    "low": float(item['low']),
                    "close": float(item['close']),
                    "volume": int(item['volume'])
                })
            
            result = {
                "code": code,
                "name": stock["name"],
                "interval": interval,
                "data": formatted_data
            }
            
            # 缓存数据
            stock_cache[cache_key] = {
                "timestamp": current_time,
                "data": result
            }
            
            return result
        except Exception as e:
            print(f"Error fetching real data: {e}")
            # 回退到模拟数据
            result = self.generate_mock_kline_data(code, stock["name"], interval, days)
            
            # 缓存模拟数据
            stock_cache[cache_key] = {
                "timestamp": current_time,
                "data": result
            }
            
            return result
    
    def generate_mock_kline_data(self, code, name, interval, days):
        """生成模拟K线数据"""
        kline_data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 生成基础价格
        base_price = random.uniform(5, 2000)
        current_price = base_price * 0.85
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # 生成随机价格波动
            change = (random.random() - 0.48) * (current_price * 0.03)
            current_price = max(current_price + change, 1)
            
            # 生成高低开收价格
            open_price = round(current_price * (0.98 + random.random() * 0.04), 2)
            high_price = round(max(current_price, open_price) * 1.02, 2)
            low_price = round(min(current_price, open_price) * 0.98, 2)
            close_price = round(current_price, 2)
            
            kline_data.append({
                "timestamp": int(date.timestamp() * 1000),
                "date": date.strftime("%Y-%m-%d"),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": random.randint(5000000, 15000000)
            })
        
        return {
            "code": code,
            "name": name,
            "interval": interval,
            "data": kline_data
        }
    
    def get_stock_realtime(self, code):
        """获取实时股票价格"""
        stock = next((s for s in STOCK_LIST if s["code"] == code), None)
        if not stock:
            return {"error": "Stock not found"}
        
        # 生成缓存键
        cache_key = f"realtime:{code}"
        current_time = datetime.now().timestamp()
        
        # 检查缓存是否有效（实时数据缓存时间较短，1分钟）
        realtime_cache_expiry = 60  # 1分钟
        if cache_key in stock_cache:
            cached_data = stock_cache[cache_key]
            if current_time - cached_data["timestamp"] < realtime_cache_expiry:
                print(f"Using cached realtime data for {code}")
                return cached_data["data"]
        
        # 尝试从外部API获取真实数据
        try:
            # 使用新浪财经API获取实时数据
            if code.startswith('6'):
                symbol = f'sh{code}'  # 沪市
            else:
                symbol = f'sz{code}'  # 深市
            
            url = f'http://hq.sinajs.cn/list={symbol}'
            import urllib.request
            response = urllib.request.urlopen(url, timeout=5)
            data = response.read().decode('gbk')
            
            # 解析数据
            parts = data.split(',')
            if len(parts) >= 4:
                name = parts[0].split('"')[-1]
                open_price = float(parts[1])
                close_price = float(parts[2])
                current_price = float(parts[3])
                high_price = float(parts[4])
                low_price = float(parts[5])
                volume = int(parts[8])
                
                change = current_price - close_price
                change_percent = (change / close_price) * 100
                
                result = {
                    "code": code,
                    "name": name,
                    "price": current_price,
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2),
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "volume": volume
                }
                
                # 缓存数据
                stock_cache[cache_key] = {
                    "timestamp": current_time,
                    "data": result
                }
                
                return result
        except Exception as e:
            print(f"Error fetching realtime data: {e}")
        
        # 回退到模拟数据
        base_price = random.uniform(5, 2000)
        change = random.uniform(-10, 10)
        change_percent = (change / base_price) * 100
        
        result = {
            "code": code,
            "name": stock["name"],
            "price": round(base_price + change, 2),
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "timestamp": int(datetime.now().timestamp() * 1000),
            "volume": random.randint(1000000, 10000000)
        }
        
        # 缓存模拟数据
        stock_cache[cache_key] = {
            "timestamp": current_time,
            "data": result
        }
        
        return result
    
    def get_chan_kline_analysis(self, code, interval, days):
        """获取缠论分析"""
        # 获取K线数据
        kline_data = self.get_stock_kline(code, interval, days)
        
        # 执行缠论分析
        analysis_result = self.analyze_chan_theory(kline_data["data"])
        
        # 整合结果
        return {
            "code": code,
            "name": kline_data["name"],
            "interval": interval,
            "kline_data": kline_data["data"],
            "chan_analysis": analysis_result
        }
    
    def analyze_chan_theory(self, kline_data):
        """执行缠论分析"""
        if not kline_data:
            return {
                "trend": "sideways",
                "pivots": [],
                "centrals": [],
                "buyPoints": [],
                "sellPoints": [],
                "segments": []
            }
        
        # 识别转折点
        pivots = []
        if len(kline_data) >= 3:
            for i in range(1, len(kline_data) - 1):
                current = kline_data[i]
                prev = kline_data[i-1]
                next_k = kline_data[i+1]
                
                # 低点转折点
                if current["low"] < prev["low"] and current["low"] < next_k["low"]:
                    pivots.append({"type": "low", "price": current["low"], "date": current["date"]})
                # 高点转折点
                elif current["high"] > prev["high"] and current["high"] > next_k["high"]:
                    pivots.append({"type": "high", "price": current["high"], "date": current["date"]})
        
        # 识别中枢
        centrals = []
        if len(kline_data) >= 5:
            i = 0
            while i + 5 <= len(kline_data):
                window = kline_data[i:i+5]
                high = max(k["high"] for k in window)
                low = min(k["low"] for k in window)
                
                # 检查是否形成中枢
                if (high - low) / low < 0.03:
                    centrals.append({
                        "start_date": window[0]["date"],
                        "end_date": window[-1]["date"],
                        "high": high,
                        "low": low,
                        "mid": (high + low) / 2,
                        "level": 1
                    })
                    i += 5
                else:
                    i += 1
        
        # 识别买卖点
        buy_points = []
        sell_points = []
        
        if centrals:
            latest_central = centrals[-1]
            latest_klines = kline_data[-20:]
            
            # 识别买点
            for kline in latest_klines:
                # 第一类买点：中枢下方的背驰
                if kline["low"] < latest_central["low"]:
                    buy_points.append({
                        "price": kline["low"],
                        "date": kline["date"],
                        "confidence": 85.0,
                        "type": "first"
                    })
                # 第二类买点：中枢下方的回调不创新低
                elif kline["low"] >= latest_central["low"] and kline["low"] < latest_central["mid"]:
                    buy_points.append({
                        "price": kline["low"],
                        "date": kline["date"],
                        "confidence": 80.0,
                        "type": "second"
                    })
                # 第三类买点：中枢上方的回调不回中枢
                elif kline["low"] > latest_central["high"]:
                    buy_points.append({
                        "price": kline["low"],
                        "date": kline["date"],
                        "confidence": 75.0,
                        "type": "third"
                    })
            
            # 识别卖点
            for kline in latest_klines:
                # 第一类卖点：中枢上方的背驰
                if kline["high"] > latest_central["high"]:
                    sell_points.append({
                        "price": kline["high"],
                        "date": kline["date"],
                        "confidence": 85.0,
                        "type": "first"
                    })
                # 第二类卖点：中枢上方的反弹不创新高
                elif kline["high"] <= latest_central["high"] and kline["high"] > latest_central["mid"]:
                    sell_points.append({
                        "price": kline["high"],
                        "date": kline["date"],
                        "confidence": 80.0,
                        "type": "second"
                    })
                # 第三类卖点：中枢下方的反弹不回中枢
                elif kline["high"] < latest_central["low"]:
                    sell_points.append({
                        "price": kline["high"],
                        "date": kline["date"],
                        "confidence": 75.0,
                        "type": "third"
                    })
        
        # 分析趋势
        trend = "sideways"
        if len(kline_data) >= 10:
            recent = kline_data[-10:]
            start_price = recent[0]["close"]
            end_price = recent[-1]["close"]
            if end_price > start_price * 1.05:
                trend = "up"
            elif end_price < start_price * 0.95:
                trend = "down"
        
        # 分析线段
        segments = []
        if len(pivots) >= 2:
            latest_pivot = pivots[-1]
            second_latest_pivot = pivots[-2]
            
            if latest_pivot["type"] == "high" and second_latest_pivot["type"] == "low":
                segments.append("当前处于上涨线段中")
            elif latest_pivot["type"] == "low" and second_latest_pivot["type"] == "high":
                segments.append("当前处于下跌线段中")
        
        return {
            "trend": trend,
            "pivots": pivots,
            "centrals": centrals,
            "buyPoints": buy_points,
            "sellPoints": sell_points,
            "segments": segments
        }

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), StockAPIHandler) as httpd:
        print(f"Stock Analysis Backend running at http://localhost:{PORT}")
        print("API Endpoints:")
        print("  GET /api/health - Health check")
        print("  GET /api/stocks - Get stock list")
        print("  GET /api/stocks/{code} - Get stock detail")
        print("  GET /api/stocks/{code}/history - Get stock history")
        print("  GET /api/stocks/{code}/kline?interval=1d&days=120 - Get stock K-line data")
        print("  GET /api/stocks/{code}/realtime - Get realtime stock price")
        print("  GET /api/analysis/chan/kline/{code}?interval=1d&days=120 - Get Chan theory analysis")
        print("\nPress Ctrl+C to stop the server")
        httpd.serve_forever()
