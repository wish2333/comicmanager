"""File-related Pydantic models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class QueuedFile(BaseModel):
    """A single file in the merge queue."""

    path: str
    name: str
    type: Literal["CBZ", "ZIP"]
    size: int
    page_count: int = 0
    valid: bool = True
    error: str | None = None


class MergeRequest(BaseModel):
    """Request body for starting a merge."""

    output_filename: str
    output_dir: str
    preserve_metadata: bool = True
    zip_formats: list[str] = Field(default_factory=lambda: ["jpg"])


class MergedFileInfo(BaseModel):
    """Info about a single file that was merged."""

    path: str
    name: str
    type: Literal["CBZ", "ZIP"]
    pages: int


class MergeResult(BaseModel):
    """Result of a merge operation."""

    success: bool
    output_path: str | None = None
    total_pages: int = 0
    merged_files: list[MergedFileInfo] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class ReorderRequest(BaseModel):
    """Request body for reordering files."""

    from_index: int
    to_index: int


class RemoveRequest(BaseModel):
    """Request body for removing files."""

    indices: list[int]


class ValidateResponse(BaseModel):
    """Response for file validation."""

    valid_count: int
    invalid_count: int
    files: list[QueuedFile]
