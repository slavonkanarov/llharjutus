"""Serve the frontend as a separate local service."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os


def main() -> None:
    port = int(os.environ.get("FRONTEND_PORT", "5173"))
    directory = str(Path(__file__).resolve().parent)
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=directory, **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Frontend listening at http://127.0.0.1:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
