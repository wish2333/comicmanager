"""File queue API routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.core.state import app_state
from src.models.files import (
    QueuedFile,
    RemoveRequest,
    ReorderRequest,
    ValidateResponse,
)
from src.services.file_info import build_queued_file
from src.services.validator import validate_comic_file

router = APIRouter()


@router.post("/api/files")
async def add_files(request: Request):
    """Add files to the merge queue. Accepts JSON body with 'paths' list."""
    body = await request.json()
    paths: list[str] = body.get("paths", [])

    if not paths:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "no file paths provided"},
        )

    added: list[QueuedFile] = []
    errors: list[str] = []

    for file_path in paths:
        is_valid, error = validate_comic_file(file_path)
        if not is_valid:
            errors.append(f"{file_path}: {error}")
            continue

        try:
            queued = build_queued_file(file_path)
            added.append(queued)
        except Exception as e:
            errors.append(f"{file_path}: {e}")

    if not added and errors:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "all files invalid", "details": errors},
        )

    updated = app_state.add_files(added)
    return {
        "success": True,
        "data": [f.model_dump() for f in updated],
        "added_count": len(added),
        "errors": errors if errors else None,
    }


@router.get("/api/files")
async def get_files():
    """Get all files currently in the merge queue."""
    files = app_state.files
    return {
        "success": True,
        "data": [f.model_dump() for f in files],
    }


@router.delete("/api/files")
async def remove_files(request: Request):
    """Remove files by indices. JSON body: {indices: [0, 1, 2]}."""
    body = await request.json()
    req = RemoveRequest(**body)
    updated = app_state.remove_by_indices(req.indices)
    return {
        "success": True,
        "data": [f.model_dump() for f in updated],
    }


@router.put("/api/files/reorder")
async def reorder_files(request: Request):
    """Reorder a file in the queue. JSON body: {from_index: 0, to_index: 3}."""
    body = await request.json()
    req = ReorderRequest(**body)
    updated = app_state.reorder(req.from_index, req.to_index)
    return {
        "success": True,
        "data": [f.model_dump() for f in updated],
    }


@router.post("/api/files/clear")
async def clear_files():
    """Clear all files from the merge queue."""
    app_state.clear_files()
    return {"success": True, "data": []}


@router.post("/api/files/validate")
async def validate_files():
    """Validate all files in the queue. Returns per-file status."""
    files = app_state.files
    validated: list[QueuedFile] = []
    valid_count = 0
    invalid_count = 0

    for f in files:
        is_valid, error = validate_comic_file(f.path)
        updated = QueuedFile(
            path=f.path,
            name=f.name,
            type=f.type,
            size=f.size,
            page_count=f.page_count,
            valid=is_valid,
            error=error if not is_valid else None,
        )
        validated.append(updated)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

    app_state.set_files(validated)

    return {
        "success": True,
        "data": {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "files": [f.model_dump() for f in validated],
        },
    }


@router.post("/api/files/sort")
async def sort_files(request: Request):
    """Sort files by name. JSON body: { key: 'name', reverse: false }."""
    body = await request.json()
    key = body.get("key", "name")
    reverse = body.get("reverse", False)

    if key == "name":
        updated = app_state.sort_by_name(reverse=reverse)
    else:
        updated = app_state.sort_by_name(reverse=reverse)

    return {
        "success": True,
        "data": [f.model_dump() for f in updated],
    }
