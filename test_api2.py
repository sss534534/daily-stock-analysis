import http.client
import json

# 测试K线数据API
conn = http.client.HTTPConnection("localhost", 3004)
conn.request("GET", "/api/stocks/600036/kline?interval=1d&days=120")
response = conn.getresponse()
data = response.read().decode('utf-8')
print(f"Status: {response.status}")
print(f"Reason: {response.reason}")
print(f"Data: {data}")
conn.close()
