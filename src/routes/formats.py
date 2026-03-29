"""Supported image formats API route."""

from __future__ import annotations

from fastapi import APIRouter

from src.core.constants import SUPPORTED_IMAGE_FORMATS

router = APIRouter()


@router.get("/api/formats")
async def get_formats():
    """Get supported image formats for ZIP extraction."""
    return {
        "success": True,
        "data": sorted(SUPPORTED_IMAGE_FORMATS),
    }
