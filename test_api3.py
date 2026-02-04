import http.client
import json

# 测试K线数据API
conn = http.client.HTTPConnection("localhost", 3004)
try:
    conn.request("GET", "/api/stocks/600036/kline?interval=1d&days=120")
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    print(f"Status: {response.status}")
    print(f"Reason: {response.reason}")
    # 尝试解析JSON数据
    try:
        json_data = json.loads(data)
        print(f"\nAPI Response (parsed):")
        print(f"Code: {json_data.get('code')}")
        print(f"Name: {json_data.get('name')}")
        print(f"Interval: {json_data.get('interval')}")
        print(f"Number of K-line data points: {len(json_data.get('data', []))}")
        if json_data.get('data'):
            print(f"First data point: {json_data['data'][0]}")
            print(f"Last data point: {json_data['data'][-1]}")
    except json.JSONDecodeError:
        print(f"\nRaw data: {data}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
