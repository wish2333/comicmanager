"""Input validation services.

Ported from comicmanager/utils/validators.py.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

from src.core.constants import (
    ILLEGAL_FILENAME_CHARS,
    MAX_FILENAME_LENGTH,
    MAX_PATH_LENGTH,
    SUPPORTED_IMAGE_EXTENSIONS,
    WINDOWS_RESERVED_NAMES,
)


def validate_filename(filename: str) -> tuple[bool, str | None]:
    """Validate a filename. Returns (is_valid, error_message)."""
    if not filename or not filename.strip():
        return False, "filename cannot be empty"

    filename = filename.strip()

    for char in ILLEGAL_FILENAME_CHARS:
        if char in filename:
            return False, f"filename contains illegal character: {char}"

    stem = Path(filename).stem.upper()
    if stem in WINDOWS_RESERVED_NAMES:
        return False, f"filename uses reserved name: {stem}"

    if len(filename) > MAX_FILENAME_LENGTH:
        return False, "filename too long (max 255 chars)"

    if filename.startswith(".") or filename.startswith(" ") or filename.endswith(".") or filename.endswith(" "):
        return False, "filename cannot start or end with dot or space"

    return True, None


def validate_directory_path(directory: str) -> tuple[bool, str | None]:
    """Validate a directory path. Returns (is_valid, error_message)."""
    if not directory or not directory.strip():
        return False, "directory path cannot be empty"

    try:
        path = Path(directory.strip())

        if any(char in str(path) for char in '<>"|?*'):
            return False, "directory path contains illegal characters"

        if path.exists() and not path.is_dir():
            return False, "specified path is not a directory"

        if len(str(path)) > MAX_PATH_LENGTH:
            return False, "path too long (max 260 chars)"

        return True, None
    except Exception as e:
        return False, f"invalid directory path: {e}"


def validate_comic_file(file_path: str) -> tuple[bool, str | None]:
    """Validate a CBZ or ZIP comic file. Returns (is_valid, error_message)."""
    if not file_path or not file_path.strip():
        return False, "file path cannot be empty"

    try:
        path = Path(file_path.strip())

        if not path.exists():
            return False, "file does not exist"
        if not path.is_file():
            return False, "specified path is not a file"
        if path.stat().st_size == 0:
            return False, "file is empty"

        suffix = path.suffix.lower()
        if suffix not in (".cbz", ".zip"):
            return False, "not a CBZ or ZIP file"

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                files = zf.namelist()
                if not files:
                    return False, "archive is empty"
                has_images = any(
                    f.lower().endswith(tuple(SUPPORTED_IMAGE_EXTENSIONS)) for f in files
                )
                if not has_images:
                    return False, "no image files found in archive"
        except zipfile.BadZipFile:
            return False, "archive is corrupted or invalid"

        return True, None
    except Exception as e:
        return False, f"validation error: {e}"


def validate_output_path(output_path: str, overwrite: bool = False) -> tuple[bool, str | None]:
    """Validate output path for the merged CBZ. Returns (is_valid, error_message)."""
    if not output_path or not output_path.strip():
        return False, "output path cannot be empty"

    try:
        path = Path(output_path.strip())

        is_valid, error = validate_filename(path.name)
        if not is_valid:
            return False, error

        is_valid, error = validate_directory_path(str(path.parent))
        if not is_valid:
            return False, error

        if path.parent.exists() and not os.access(path.parent, os.W_OK):
            return False, "directory is not writable"

        if path.exists():
            if not overwrite:
                return False, f"file already exists: {path.name}"
            if not path.is_file():
                return False, "target exists but is not a file"

        if path.suffix.lower() != ".cbz":
            return False, "output must use .cbz extension"

        return True, None
    except Exception as e:
        return False, f"output path validation error: {e}"
