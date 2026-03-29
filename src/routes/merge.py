"""Merge operation API routes."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from src.core.state import app_state
from src.models.files import MergeRequest
from src.models.progress import MergeProgressEvent
from src.services.file_info import get_unique_filename
from src.services.validator import validate_output_path
from src.tasks.merge_task import merge_task_manager

router = APIRouter()


@router.post("/api/merge")
async def start_merge(request: Request):
    """Start a merge operation. Returns task_id for SSE progress."""
    body = await request.json()
    req = MergeRequest(**body)

    if app_state.active_task_id:
        return JSONResponse(
            status_code=409,
            content={"success": False, "error": "a merge is already in progress"},
        )

    files = app_state.files
    if not files:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "no files in queue"},
        )

    file_paths = [f.path for f in files]

    output_path = get_unique_filename(req.output_dir, req.output_filename, ".cbz")
    full_output_path = str(
        __import__("pathlib").Path(req.output_dir) / output_path
    )

    is_valid, error = validate_output_path(full_output_path)
    if not is_valid:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": error},
        )

    zip_formats = set(fmt.lower() for fmt in req.zip_formats) if req.zip_formats else {"jpg"}

    # Run merge in background and stream progress via SSE
    app_state.set_active_task_id("pending")

    async def merge_and_stream():
        from pathlib import Path

        queue = asyncio.Queue[MergeProgressEvent]()

        def callback(event: MergeProgressEvent):
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(queue.put_nowait, event)
            except RuntimeError:
                pass

        loop = asyncio.get_event_loop()

        async def do_merge():
            from src.services.merger import merge_comic_files
            result = await loop.run_in_executor(
                None,
                lambda: merge_comic_files(
                    file_paths=file_paths,
                    output_path=full_output_path,
                    task_id="merge",
                    preserve_metadata=req.preserve_metadata,
                    zip_formats=zip_formats,
                    progress_callback=callback,
                ),
            )
            return result

        task = asyncio.create_task(do_merge())

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.5)
                yield {"data": event.model_dump_json()}
                if event.stage in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                if task.done():
                    # Drain remaining queue events
                    while not queue.empty():
                        event = queue.get_nowait()
                        yield {"data": event.model_dump_json()}
                        if event.stage in ("done", "error"):
                            break
                    break

        result = await task
        yield {"data": result.model_dump_json()}
        app_state.set_active_task_id(None)

    return EventSourceResponse(merge_and_stream())


@router.get("/api/merge/{task_id}/progress")
async def merge_progress(task_id: str):
    """SSE endpoint for merge progress. (Kept for reference; POST /api/merge streams directly.)"""
    queue = merge_task_manager.get_progress_queue(task_id)
    if not queue:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "task not found"},
        )

    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {"data": event.model_dump_json()}
                if event.stage in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": ""}
                break

    return EventSourceResponse(event_generator())
