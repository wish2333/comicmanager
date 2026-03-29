"""ComicManager Neo entry point - starts FastAPI server and PyWebView window."""

from __future__ import annotations

import logging
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Callable

import uvicorn
import webview

logger = logging.getLogger("comicmanager_neo")

DEV_MODE = False
DEV_PORT = 8901


def _find_free_port(host: str = "127.0.0.1") -> int:
    """Find a free port by binding to port 0."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 10.0) -> bool:
    """Poll the health endpoint until the server is ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1)
            return True
        except (urllib.error.URLError, OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


def _start_server(port: int) -> Callable[[], None]:
    """Start uvicorn in a background thread. Returns a shutdown callback."""
    from src.server import create_app

    app = create_app()
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    def shutdown() -> None:
        server.should_exit = True

    return shutdown


def main() -> None:
    """Application entry point."""
    if sys.version_info < (3, 10):
        print("Python 3.10 or higher is required.")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    global DEV_MODE
    DEV_MODE = "--dev" in sys.argv

    if DEV_MODE:
        port = DEV_PORT
        print(f"[DEV] Starting development server on port {port}")
    else:
        port = _find_free_port()

    shutdown = _start_server(port)
    print(f"Starting ComicManager Neo on http://127.0.0.1:{port}")

    if not _wait_for_server(port):
        print("Failed to start server. Exiting.")
        sys.exit(1)

    from src.js_api import JsApi, setup_drag_drop

    url = f"http://127.0.0.1:{port}"
    api = JsApi()

    if DEV_MODE:
        webview.create_window(
            "ComicManager Neo",
            "http://localhost:5173",
            width=800,
            height=1000,
            min_size=(600, 800),
            js_api=api,
        )
    else:
        webview.create_window(
            "ComicManager Neo",
            url,
            width=800,
            height=1000,
            min_size=(600, 800),
            js_api=api,
        )

    # Set up native file drag-and-drop via pywebview's DOM event system.
    # This registers a drop handler that captures real OS file paths.
    setup_drag_drop(api)

    try:
        webview.start(debug=DEV_MODE)
    finally:
        shutdown()
        print("ComicManager Neo has shut down.")


if __name__ == "__main__":
    main()
