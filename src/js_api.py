"""Python API class exposed to pywebview JavaScript bridge.

Provides native OS file/directory dialogs via pywebview's create_file_dialog API.
File drag-and-drop is handled via pywebview's DOM event system.
"""

from __future__ import annotations

import threading
from typing import Any


class JsApi:
    """Python API exposed to the frontend via window.pywebview.api."""

    def __init__(self) -> None:
        self._dropped_paths: list[str] = []
        self._drop_lock = threading.Lock()

    def open_files(self, initial_dir: str = "") -> dict[str, Any]:
        """Open native file picker dialog. Returns dict with 'paths' list."""
        import webview

        if initial_dir:
            from pathlib import Path
            if not Path(initial_dir).exists():
                initial_dir = ""

        try:
            result = webview.windows[0].create_file_dialog(
                dialog_type=webview.FileDialog.OPEN,
                directory=initial_dir,
                allow_multiple=True,
                file_types=(
                    "Comic Files (*.cbz;*.zip)",
                    "CBZ Files (*.cbz)",
                    "ZIP Files (*.zip)",
                    "All Files (*.*)",
                ),
            )
        except (IndexError, AttributeError):
            return {"success": False, "data": [], "error": "No webview window"}

        if result is None:
            return {"success": True, "data": []}

        paths = [str(p) for p in result]
        return {"success": True, "data": paths}

    def open_directory(self, initial_dir: str = "") -> dict[str, Any]:
        """Open native directory picker dialog. Returns dict with 'path' string or null."""
        import webview

        if initial_dir:
            from pathlib import Path
            if not Path(initial_dir).exists():
                initial_dir = ""

        try:
            result = webview.windows[0].create_file_dialog(
                dialog_type=webview.FileDialog.FOLDER,
                directory=initial_dir,
            )
        except (IndexError, AttributeError):
            return {"success": False, "data": None, "error": "No webview window"}

        if result is None:
            return {"success": True, "data": None}

        return {"success": True, "data": str(result[0]) if result else None}

    def get_dropped_files(self) -> dict[str, Any]:
        """Return file paths from the most recent drop event and clear the buffer."""
        with self._drop_lock:
            paths = list(self._dropped_paths)
            self._dropped_paths.clear()
        return {"success": True, "data": paths}

    def _on_drop(self, event: dict) -> None:
        """Internal callback invoked by pywebview's DOM event system.

        Receives a drop event dict where each file object has a
        'pywebviewFullPath' key injected by pywebview.
        """
        files = event.get("dataTransfer", {}).get("files", [])
        paths: list[str] = []
        for f in files:
            full_path = f.get("pywebviewFullPath")
            if full_path:
                paths.append(full_path)

        if paths:
            with self._drop_lock:
                self._dropped_paths.extend(paths)


def setup_drag_drop(api: JsApi) -> None:
    """Set up pywebview's native file drag-and-drop handling.

    Must be called before webview.start(). Injects JavaScript that
    bridges browser drop events to pywebview's CoreWebView2File
    path extraction pipeline.
    """
    import webview

    def on_loaded():
        """Register drop event handler after the window is fully loaded."""
        from webview.dom import DOMEventHandler

        window = webview.windows[0]

        # Register the document drop handler via pywebview's DOM API.
        # Using DOMEventHandler enables prevent_default so the browser
        # doesn't navigate to the dropped file.
        # This also increments _dnd_state['num_listeners'] automatically.
        doc = window.dom.document
        handler = DOMEventHandler(api._on_drop, prevent_default=True)
        doc.on("drop", handler)

    window = webview.windows[0]
    window.events.loaded += on_loaded
