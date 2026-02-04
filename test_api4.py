import http.client
import json

# 测试健康检查API
conn = http.client.HTTPConnection("localhost", 3004)
try:
    conn.request("GET", "/api/health")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"Health Check - Status: {response.status}")
    print(f"Health Check - Data: {data}")
    
    # 测试股票列表API
    conn.request("GET", "/api/stocks")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"\nStock List - Status: {response.status}")
    print(f"Stock List - Data: {data}")
    
    # 测试K线数据API
    conn.request("GET", "/api/stocks/600036/kline?interval=1d&days=120")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"\nK-line Data - Status: {response.status}")
    print(f"K-line Data - Data: {data}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
