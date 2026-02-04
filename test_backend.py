#!/usr/bin/env python3
"""
测试后端服务的基本功能
"""
import http.server
import socketserver
import json

PORT = 3005

class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/api/health':
            response = {'status': 'ok', 'message': 'Health check passed'}
        else:
            response = {'status': 'error', 'message': 'Endpoint not found'}
        
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == "__main__":
    print(f"Starting test server on port {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
            print(f"Test server running at http://localhost:{PORT}")
            print("Testing server stability...")
            # 运行10秒后退出
            import time
            start_time = time.time()
            while time.time() - start_time < 10:
                httpd.handle_request()
            print("Test server stopped after 10 seconds")
    except Exception as e:
        print(f"Error starting server: {e}")
