"""Protected AI service placeholder; the demo does not request AI review."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "reviewAvailable": False})
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/internal/v1/review":
            self._json(404, {"error": "not_found"})
            return
        token = os.environ.get("AI_SERVICE_TOKEN")
        if not token or self.headers.get("Authorization") != f"Bearer {token}":
            self._json(401, {"error": "unauthorized"})
            return
        self._json(501, {"error": "review_unavailable"})


def main() -> None:
    port = int(os.environ.get("AI_SERVICE_PORT", "8001"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"AI boundary listening at http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
