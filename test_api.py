import urllib.request
import json

# 测试K线数据API
url = "http://localhost:3004/api/stocks/600036/kline?interval=1d&days=120"

print(f"Testing API: {url}")
try:
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')
        json_data = json.loads(data)
        print("API Response:")
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        print(f"\nNumber of K-line data points: {len(json_data.get('data', []))}")
except Exception as e:
    print(f"Error: {e}")
