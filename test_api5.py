import http.client
import json

# 测试后端API端点
conn = http.client.HTTPConnection("localhost", 3006)
try:
    # 测试健康检查API
    print("测试健康检查API...")
    conn.request("GET", "/api/health")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"Health Check - Status: {response.status}")
    print(f"Health Check - Data: {data}")
    
    # 测试股票列表API
    print("\n测试股票列表API...")
    conn.request("GET", "/api/stocks")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"Stock List - Status: {response.status}")
    print(f"Stock List - Data: {data}")
    
    # 测试K线数据API
    print("\n测试K线数据API...")
    conn.request("GET", "/api/stocks/600036/kline?interval=1d&days=120")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"K-line Data - Status: {response.status}")
    # 尝试解析JSON数据
    try:
        json_data = json.loads(data)
        print(f"K-line Data - Parsed: {json_data}")
        print(f"Number of K-line data points: {len(json_data.get('data', []))}")
    except json.JSONDecodeError:
        print(f"K-line Data - Raw: {data}")
    
    # 测试投资组合API
    print("\n测试投资组合API...")
    conn.request("GET", "/api/portfolio")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"Portfolio - Status: {response.status}")
    print(f"Portfolio - Data: {data}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
