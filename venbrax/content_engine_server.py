"""
VenBraX Content Engine — HTTP Server
Expone el motor de contenido para que n8n lo consuma vía HTTP Request.
Solo librería estándar — cero dependencias externas.

GET /generate                    -> genera las 5 plataformas
GET /generate?platform=linkedin  -> genera solo una
GET /generate?use_claude=true    -> usa Claude Opus para redactar
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_engine import get_insight_of_day, format_for_platform, generate_with_claude, PLATFORMS


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._json(200, {"status": "ok"})
            return

        if parsed.path != "/generate":
            self._json(404, {"error": "not found"})
            return

        params = parse_qs(parsed.query)
        use_claude = params.get("use_claude", ["false"])[0].lower() == "true"
        platform_filter = params.get("platform", [None])[0]

        insight = get_insight_of_day()
        platforms = [platform_filter] if platform_filter in PLATFORMS else list(PLATFORMS.keys())

        posts = {}
        for p in platforms:
            if use_claude and os.environ.get("ANTHROPIC_API_KEY"):
                posts[p] = generate_with_claude(insight, p)
            else:
                posts[p] = format_for_platform(insight, p)

        self._json(200, {
            "insight_id": insight["id"],
            "insight_title": insight["title"],
            "posts": posts,
        })

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[content-engine] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[VenBraX] Content Engine API escuchando en :{port}")
    server.serve_forever()
