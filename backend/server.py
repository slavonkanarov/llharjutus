"""Dependency-free HTTP API for the local demo."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .service import ApiError, LessonService


ALLOWED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


def create_handler(service: LessonService):
    class Handler(BaseHTTPRequestHandler):
        def _headers(self, status: int, content_length: int) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(content_length))
            self.send_header("Cache-Control", "no-store")
            origin = self.headers.get("Origin")
            if origin in ALLOWED_ORIGINS:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()

        def _json(self, status: int, payload: dict) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._headers(status, len(data))
            self.wfile.write(data)

        def _handle(self) -> None:
            try:
                path = urlparse(self.path).path
                if path == "/health" and self.command == "GET":
                    self._json(200, {"status": "ok"})
                    return
                learner = service.learner_for_token(self.headers.get("Authorization"))
                if self.command == "GET" and path == "/api/v1/lessons/estonian-first-words":
                    self._json(200, service.lesson(learner, "estonian-first-words"))
                elif self.command == "GET" and path == "/api/v1/progress":
                    self._json(200, service.progress(learner))
                elif self.command == "POST" and path == "/api/v1/attempts":
                    length = int(self.headers.get("Content-Length", "0"))
                    if not 0 < length <= 16384:
                        raise ApiError(413, "invalid_request", "Request body is empty or too large.")
                    try:
                        payload = json.loads(self.rfile.read(length))
                    except (ValueError, UnicodeDecodeError):
                        raise ApiError(400, "invalid_json", "Invalid JSON body.") from None
                    self._json(200, service.submit(learner, payload))
                elif self.command == "POST" and path == "/api/v1/demo/reset":
                    self._json(200, service.reset_demo(learner))
                else:
                    raise ApiError(404, "not_found", "Endpoint not found.")
            except ApiError as error:
                self._json(error.status, {"error": {"code": error.code, "message": error.message}})
            except ValueError:
                self._json(400, {"error": {"code": "invalid_request", "message": "Invalid request."}})

        def do_GET(self) -> None:
            self._handle()

        def do_POST(self) -> None:
            self._handle()

        def do_OPTIONS(self) -> None:
            self._headers(204, 0)

    return Handler


def main() -> None:
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), create_handler(LessonService()))
    print(f"Backend listening at http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
