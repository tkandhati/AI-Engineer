"""
Local proxy for Anthropic API — run this before opening index.html.

Usage:
  Windows:  set ANTHROPIC_KEY=sk-ant-...  && python proxy.py
  Mac/Linux: ANTHROPIC_KEY=sk-ant-... python proxy.py

Then open: http://localhost:8080/index.html  (served by python -m http.server 8080)
"""

import http.server
import json
import os
import urllib.request
import urllib.error

PORT = 5001
KEY = os.environ.get('ANTHROPIC_KEY', '')


class Handler(http.server.BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            headers={
                'x-api-key': KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req) as r:
                resp = r.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._cors()
                self.end_headers()
                self.wfile.write(resp)
        except urllib.error.HTTPError as e:
            resp = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(resp)

    def log_message(self, fmt, *args):
        print(f"[proxy] {args[0]} {args[1]}")


if __name__ == '__main__':
    if not KEY:
        print("ERROR: set the ANTHROPIC_KEY environment variable before running.")
        raise SystemExit(1)
    print(f"Proxy running on http://localhost:{PORT}")
    print("Keep this terminal open while using the page.")
    http.server.HTTPServer(('', PORT), Handler).serve_forever()
