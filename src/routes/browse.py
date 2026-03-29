"""OS file/directory browse API routes."""

from __future__ import annotations

import os
import tempfile
import tkinter as tk
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


def _create_tk_root():
    """Create a hidden Tk root window for file dialogs."""
    root = tk.Tk()
    root.withdraw()
    return root


@router.post("/api/browse/files")
async def browse_files(request: Request):
    """Open an OS file picker dialog. Returns list of selected file paths."""
    body = await request.json() or {}
    initial_dir = body.get("initial_dir", "")
    file_types = body.get(
        "file_types",
        [("Comic files", "*.cbz *.zip"), ("CBZ files", "*.cbz"), ("ZIP files", "*.zip"), ("All files", "*.*")],
    )

    try:
        root = _create_tk_root()
        file_paths = tk.filedialog.askopenfilenames(
            parent=root,
            title="Select comic files",
            initialdir=initial_dir if initial_dir and Path(initial_dir).exists() else None,
            filetypes=file_types,
        )
        root.destroy()

        paths = list(file_paths)
        return {"success": True, "data": paths}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.post("/api/browse/directory")
async def browse_directory(request: Request):
    """Open an OS directory picker dialog. Returns selected directory path."""
    body = await request.json() or {}
    initial_dir = body.get("initial_dir", "")

    try:
        root = _create_tk_root()
        directory = tk.filedialog.askdirectory(
            parent=root,
            title="Select output directory",
            initialdir=initial_dir if initial_dir and Path(initial_dir).exists() else None,
        )
        root.destroy()

        if not directory:
            return {"success": True, "data": None}

        return {"success": True, "data": directory}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )
