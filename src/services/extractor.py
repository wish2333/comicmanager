"""ZIP image extraction service.

Ported from comicmanager/core/zip_extractor.py.
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from src.core.constants import (
    MAX_IMAGE_SIZE_BYTES,
    SUPPORTED_IMAGE_FORMATS,
)
from src.services.file_info import natural_sort_key


def validate_zip_file(zip_path: str) -> dict[str, Any]:
    """Validate a ZIP file and scan for images. Returns validation result dict."""
    result: dict[str, Any] = {
        "valid": False,
        "error": None,
        "image_files": [],
        "total_files": 0,
        "supported_formats": set(),
        "file_size": 0,
    }

    try:
        path = Path(zip_path)
        if not path.exists() or not path.is_file():
            result["error"] = "file does not exist"
            return result
        if path.suffix.lower() != ".zip":
            result["error"] = "not a ZIP file"
            return result

        result["file_size"] = path.stat().st_size

        with zipfile.ZipFile(zip_path, "r") as zf:
            file_list = zf.namelist()
            result["total_files"] = len(file_list)

            image_files = []
            for name in file_list:
                if not name or name.endswith("/"):
                    continue
                if ".." in name or name.startswith("/"):
                    continue

                ext = Path(name).suffix.lower().lstrip(".")
                if ext in SUPPORTED_IMAGE_FORMATS:
                    file_info = zf.getinfo(name)
                    if file_info.file_size > MAX_IMAGE_SIZE_BYTES:
                        continue

                    image_files.append({
                        "name": name,
                        "path": name,
                        "extension": ext,
                        "size": file_info.file_size,
                        "compressed_size": file_info.compress_size,
                        "date_time": file_info.date_time,
                    })
                    result["supported_formats"].add(ext)

            image_files.sort(key=lambda f: natural_sort_key(f["name"]))
            result["image_files"] = image_files

            if image_files:
                result["valid"] = True
                result["supported_formats"] = SUPPORTED_IMAGE_FORMATS.copy()
            else:
                result["error"] = "no supported image files found in ZIP (JPG, PNG, WEBP, GIF, BMP)"

    except zipfile.BadZipFile:
        result["error"] = "ZIP file is corrupted or invalid"
    except PermissionError:
        result["error"] = "permission denied"
    except UnicodeDecodeError:
        result["error"] = "invalid filename encoding in ZIP"
    except Exception as e:
        result["error"] = f"error validating ZIP: {e}"

    return result


def extract_images(
    zip_path: str,
    output_dir: str,
    image_formats: set[str] | None = None,
    chapter_prefix: str = "ch1",
) -> dict[str, Any]:
    """Extract images from a ZIP file to an output directory.

    Returns result dict with success, extracted_files, total_extracted.
    """
    if image_formats is None:
        image_formats = {"jpg"}

    result: dict[str, Any] = {
        "success": False,
        "error": None,
        "extracted_files": [],
        "total_extracted": 0,
    }

    try:
        zip_path = os.path.normpath(zip_path)
        path = Path(zip_path)
        if not path.exists() or not path.is_file():
            result["error"] = "ZIP file does not exist"
            return result
        if path.suffix.lower() != ".zip":
            result["error"] = "not a ZIP file"
            return result

        validation = validate_zip_file(zip_path)
        if not validation["valid"]:
            result["error"] = validation["error"]
            return result

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            target_files = [
                img for img in validation["image_files"]
                if img["extension"] in image_formats
            ]

            if not target_files:
                result["error"] = f"no images with specified formats found: {', '.join(image_formats)}"
                return result

            extracted_count = 0
            for i, img_file in enumerate(target_files):
                zip_filename = img_file["name"]
                try:
                    with zf.open(zip_filename) as f:
                        image_data = f.read()

                    ext = img_file["extension"]
                    new_name = f"{chapter_prefix}_{i + 1:03d}.{ext}"
                    new_path = Path(output_dir) / new_name

                    with open(new_path, "wb") as out_f:
                        out_f.write(image_data)

                    extracted_count += 1
                    result["extracted_files"].append(new_name)
                except Exception:
                    continue

            result["success"] = True
            result["total_extracted"] = extracted_count

    except zipfile.BadZipFile:
        result["error"] = "ZIP file is corrupted"
    except PermissionError:
        result["error"] = "permission denied"
    except Exception as e:
        result["error"] = f"extraction error: {e}"

    return result


def parse_format_string(format_string: str) -> set[str]:
    """Parse a comma-separated format string into a set of formats."""
    if not format_string:
        return {"jpg"}

    formats: set[str] = set()
    for fmt in format_string.split(","):
        fmt = fmt.strip().lstrip(".")
        if fmt in SUPPORTED_IMAGE_FORMATS:
            formats.add(fmt)

    return formats if formats else {"jpg"}
