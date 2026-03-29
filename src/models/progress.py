"""Progress event models for SSE streaming."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MergeProgressEvent(BaseModel):
    """A single progress event emitted during merge."""

    task_id: str
    stage: Literal["validating", "extracting", "merging", "writing", "done", "error"]
    current_file: str | None = None
    current_index: int = 0
    total_files: int = 0
    current_page: int = 0
    total_pages: int = 0
    message: str
