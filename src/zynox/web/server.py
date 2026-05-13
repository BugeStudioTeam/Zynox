#!/usr/bin/env python3
"""Simple web server for ZynoxAI"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

HTML = '''<!DOCTYPE html>
<html>
<head><title>ZynoxAI</title>
<style>
body{font-family:monospace;background:#0a0e27;color:#00d4ff;text-align:center;padding:50px}
h1{font-size:3rem;background:linear-gradient(135deg,#00d4ff,#9d4edd);-webkit-background-clip:text;background-clip:text;color:transparent}
.status{color:#00ff9d;margin:20px}
</style>
</head>
<body>
<h1>ZynoxAI</h1>
<div class="status">✅ Web Server Running</div>
<p>Version 2.2.5 | Buge Studio</p>
<p>Access: <a href="/api/status">/api/status</a></p>
</body>
</html>
'''

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'running', 'version': '2.2.5'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_web_server(host='127.0.0.1', port=5000, debug=False):
    server = HTTPServer((host, port), Handler)
    print(f"\n[Web Server Started]")
    print(f"[Access at: http://{host}:{port}]")
    print(f"[Press Ctrl+C to stop]\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server stopped]")