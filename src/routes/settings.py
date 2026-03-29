"""Settings API routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.core.config import get_config, update_config

router = APIRouter()

_SETTINGS_KEY_MAP = {
    "last_output_dir": ("output", "default_dir"),
    "last_input_dir": ("output", "last_input_dir"),
    "zip_image_formats": ("zip_extraction", "default_formats"),
    "theme": ("ui", "theme"),
    "preserve_metadata": ("output", "preserve_metadata"),
    "auto_increment": ("output", "auto_increment"),
}


def _extract_settings(config: dict) -> dict:
    """Extract flat settings dict from nested config."""
    from pathlib import Path
    output = config.get("output", {})
    zip_ext = config.get("zip_extraction", {})
    ui = config.get("ui", {})

    return {
        "last_output_dir": output.get("default_dir", str(Path.home())),
        "last_input_dir": output.get("last_input_dir", ""),
        "zip_image_formats": zip_ext.get("default_formats", ["jpg"]),
        "theme": ui.get("theme", "light"),
        "preserve_metadata": output.get("preserve_metadata", True),
        "auto_increment": output.get("auto_increment", True),
    }


def _apply_settings_to_config(config: dict, settings: dict) -> dict:
    """Apply flat settings to nested config structure."""
    updates: dict = {}

    for key, (section, field) in _SETTINGS_KEY_MAP.items():
        if key in settings and settings[key] is not None:
            if section not in updates:
                updates[section] = {}
            updates[section][field] = settings[key]

    return updates


@router.get("/api/settings")
async def get_settings():
    """Get current application settings."""
    config = get_config()
    settings = _extract_settings(config)
    return {"success": True, "data": settings}


@router.put("/api/settings")
async def put_settings(request: Request):
    """Update application settings."""
    body = await request.json()
    updates = _apply_settings_to_config(get_config(), body)
    if not updates:
        return {"success": True, "data": _extract_settings(get_config())}

    updated = update_config(updates)
    settings = _extract_settings(updated)
    return {"success": True, "data": settings}
