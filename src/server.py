"""FastAPI application factory."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.routes import health, files, merge, browse, settings, formats


def _get_frontend_dist() -> Path | None:
    """Locate the frontend dist directory for production static serving."""
    candidates: list[Path] = []
    # PyInstaller frozen mode
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        candidates.append(Path(sys._MEIPASS) / "frontend" / "dist")
    # Dev: project root / frontend / dist
    candidates.append(Path(__file__).resolve().parent.parent / "frontend" / "dist")
    # Env override
    env_path = os.environ.get("FRONTEND_DIST", "")
    if env_path:
        candidates.append(Path(env_path))
    for p in candidates:
        if p.exists() and (p / "index.html").exists():
            return p
    return None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="ComicManager Neo", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})

    # Register route modules
    app.include_router(health.router)
    app.include_router(files.router)
    app.include_router(merge.router)
    app.include_router(browse.router)
    app.include_router(settings.router)
    app.include_router(formats.router)

    # Production static file serving with SPA fallback
    frontend_dist = _get_frontend_dist()
    if frontend_dist:
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve the SPA - return index.html for all non-API routes."""
            file_path = frontend_dist / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))

    return app
