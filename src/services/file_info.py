"""File metadata extraction and utility services.

Ported from comicmanager/core/file_utils.py.
"""

from __future__ import annotations

import os
import re
import zipfile
from pathlib import Path

from src.core.constants import (
    ILLEGAL_FILENAME_CHARS,
    MAX_IMAGE_SIZE_BYTES,
    SUPPORTED_IMAGE_EXTENSIONS,
)
from src.models.files import QueuedFile


def is_valid_cbz_file(file_path: str) -> bool:
    """Check if the file is a valid CBZ file."""
    try:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return False
        if path.suffix.lower() != ".cbz":
            return False
        with zipfile.ZipFile(file_path, "r") as zf:
            zf.namelist()
            return True
    except Exception:
        return False


def is_valid_zip_file(file_path: str) -> bool:
    """Check if the file is a valid ZIP containing images."""
    try:
        file_path = os.path.normpath(file_path)
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            return False
        if path.suffix.lower() != ".zip":
            return False
        with zipfile.ZipFile(file_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue
                if ".." in name or name.startswith("/"):
                    continue
                if Path(name).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                    return True
            return False
    except Exception:
        return False


def get_file_type(file_path: str) -> str:
    """Determine file type: CBZ, ZIP, or UNKNOWN."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".cbz":
        return "CBZ"
    if suffix == ".zip":
        if is_valid_cbz_file(file_path):
            return "CBZ"
        if is_valid_zip_file(file_path):
            return "ZIP"
    return "UNKNOWN"


def extract_comic_info(file_path: str) -> dict:
    """Extract comic file metadata (CBZ or ZIP)."""
    with zipfile.ZipFile(file_path, "r") as zf:
        file_list = zf.namelist()

        comic_info = None
        for name in file_list:
            if name.lower().endswith("comicinfo.xml"):
                try:
                    comic_info = zf.read(name).decode("utf-8")
                except Exception:
                    pass
                break

        image_files = sorted(
            f
            for f in file_list
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"))
        )

        return {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "file_type": get_file_type(file_path),
            "file_size": Path(file_path).stat().st_size,
            "page_count": len(image_files),
            "image_files": image_files,
            "comic_info": comic_info,
            "total_files": len(file_list),
        }


def sanitize_filename(filename: str) -> str:
    """Remove illegal characters from a filename."""
    for char in ILLEGAL_FILENAME_CHARS:
        filename = filename.replace(char, "_")
    filename = filename.strip(" .")
    return filename if filename else "unnamed"


def get_unique_filename(directory: str, base_name: str, extension: str = ".cbz") -> str:
    """Generate a unique filename to avoid conflicts."""
    base_path = Path(directory)
    base_name = sanitize_filename(base_name)
    counter = 1
    filename = f"{base_name}{extension}"
    while (base_path / filename).exists():
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return filename


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable file size string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def build_queued_file(file_path: str) -> QueuedFile:
    """Build a QueuedFile from a path by extracting metadata."""
    info = extract_comic_info(file_path)
    return QueuedFile(
        path=file_path,
        name=info["file_name"],
        type=info["file_type"],
        size=info["file_size"],
        page_count=info["page_count"],
        valid=True,
        error=None,
    )


def natural_sort_key(filename: str) -> list:
    """Generate a sort key that sorts numbers naturally (page2 < page10)."""
    parts = filename.split("/")
    name = parts[-1] if parts else filename
    result: list = []
    for text in re.split(r"(\d+)", name):
        if text.isdigit():
            result.append(int(text))
        else:
            result.append(text.lower())
    return result
