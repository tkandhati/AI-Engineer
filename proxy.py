"""
Local proxy — Anthropic API + RSS feed fetcher + file-based content cache.

Usage:
  Windows:  set ANTHROPIC_KEY=sk-ant-... && python proxy.py
  Mac/Linux: ANTHROPIC_KEY=sk-ant-... python proxy.py

Endpoints:
  POST /claude          →  forwards to api.anthropic.com/v1/messages
  GET  /rss?url=...     →  fetches any RSS/Atom feed (CORS-safe)
  GET  /cache?id=...    →  reads  cache/{id}.json  (generated subtopic content)
  POST /cache           →  writes cache/{id}.json  body: {"id":"...", "data":{...}}
"""

import http.server
import json
import os
import re
import urllib.request
import urllib.error
import urllib.parse

PORT      = 5001
KEY       = os.environ.get('ANTHROPIC_KEY', '')
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')

_SAFE_ID = re.compile(r'^[\w.\-]+$')   # letters, digits, _ . - only


def _safe_id(id_: str) -> bool:
    return bool(id_) and bool(_SAFE_ID.match(id_)) and '..' not in id_


class Handler(http.server.BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _json(self, code: int, body: bytes):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── POST ─────────────────────────────────────────────────────────────────
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)

        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/cache':
            self._cache_write(body)
        else:
            self._claude_proxy(body)

    def _claude_proxy(self, body: bytes):
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            headers={
                'x-api-key':          KEY,
                'anthropic-version':  '2023-06-01',
                'content-type':       'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=360) as r:
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

    def _cache_write(self, body: bytes):
        try:
            payload = json.loads(body)
            id_  = str(payload.get('id', ''))
            data = payload.get('data', {})
            if not _safe_id(id_):
                self._json(400, b'{"error":"invalid id"}')
                return
            os.makedirs(CACHE_DIR, exist_ok=True)
            path = os.path.join(CACHE_DIR, f'{id_}.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._json(200, b'{"ok":true}')
        except Exception as e:
            self._json(500, json.dumps({'error': str(e)}).encode())

    # ── GET ──────────────────────────────────────────────────────────────────
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs     = urllib.parse.parse_qs(parsed.query)

        if parsed.path.startswith('/cache'):
            self._cache_read(qs)
        elif parsed.path.startswith('/rss'):
            self._rss_proxy(qs)
        else:
            self.send_response(404)
            self.end_headers()

    def _cache_read(self, qs: dict):
        id_ = qs.get('id', [''])[0]
        if not _safe_id(id_):
            self._json(400, b'{"error":"invalid id"}')
            return
        path = os.path.join(CACHE_DIR, f'{id_}.json')
        if not os.path.exists(path):
            self._json(404, b'{"error":"not found"}')
            return
        with open(path, 'rb') as f:
            data = f.read()
        self._json(200, data)

    def _rss_proxy(self, qs: dict):
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
        print(f'[proxy] {args[0]} {args[1]}')


if __name__ == '__main__':
    if not KEY:
        print('ERROR: set ANTHROPIC_KEY before running.')
        raise SystemExit(1)
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f'Proxy on http://localhost:{PORT}  |  cache → {CACHE_DIR}')
    print('Keep this terminal open.')
    http.server.HTTPServer(('', PORT), Handler).serve_forever()
