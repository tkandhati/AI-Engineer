"""
Local proxy — Anthropic API + RSS feed fetcher.

Usage:
  Windows:  set ANTHROPIC_KEY=sk-ant-... && python proxy.py
  Mac/Linux: ANTHROPIC_KEY=sk-ant-... python proxy.py

Endpoints:
  POST /claude          →  forwards to api.anthropic.com/v1/messages
  GET  /rss?url=...     →  fetches any RSS/Atom feed (CORS-safe)
"""

import http.server
import os
import urllib.request
import urllib.error
import urllib.parse

PORT = 5001
KEY  = os.environ.get('ANTHROPIC_KEY', '')


class Handler(http.server.BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── Claude proxy ──────────────────────────────────────────────────────────
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)
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

    # ── RSS feed proxy ────────────────────────────────────────────────────────
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if not parsed.path.startswith('/rss'):
            self.send_response(404)
            self.end_headers()
            return

        qs  = urllib.parse.parse_qs(parsed.query)
        url = qs.get('url', [''])[0]
        if not url:
            self.send_response(400)
            self._cors()
            self.end_headers()
            self.wfile.write(b'Missing url parameter')
            return

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; AIEngineerBot/1.0)'},
        )
        try:
            with urllib.request.urlopen(req, timeout=6) as r:
                resp = r.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml; charset=utf-8')
                self._cors()
                self.end_headers()
                self.wfile.write(resp)
        except Exception as e:
            self.send_response(502)
            self._cors()
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        print(f"[proxy] {args[0]} {args[1]}")


if __name__ == '__main__':
    if not KEY:
        print("ERROR: set ANTHROPIC_KEY before running.")
        raise SystemExit(1)
    print(f"Proxy running on http://localhost:{PORT}  (Claude + RSS)")
    print("Keep this terminal open.")
    http.server.HTTPServer(('', PORT), Handler).serve_forever()
