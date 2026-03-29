"""CBZ/ZIP merge service.

Ported from comicmanager/core/cbz_merger.py.
"""

from __future__ import annotations

import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Callable

from src.models.files import MergeResult
from src.models.progress import MergeProgressEvent
from src.services.extractor import extract_images
from src.services.file_info import extract_comic_info, get_file_type


def _report_progress(
    event: MergeProgressEvent,
    callback: Callable[[MergeProgressEvent], None] | None,
) -> None:
    """Send progress event if callback is set."""
    if callback:
        callback(event)


def validate_comic_files(file_paths: list[str]) -> dict[str, Any]:
    """Validate comic files (CBZ and ZIP). Returns validation result dict."""
    results: dict[str, Any] = {
        "valid_files": [],
        "invalid_files": [],
        "total_size": 0,
        "total_pages": 0,
        "errors": [],
    }

    for file_path in file_paths:
        try:
            info = extract_comic_info(file_path)
            if info["file_type"] == "UNKNOWN":
                results["invalid_files"].append({
                    "path": file_path,
                    "error": "not a valid comic file (CBZ or ZIP)",
                })
                continue

            results["valid_files"].append(info)
            results["total_size"] += info["file_size"]
            results["total_pages"] += info["page_count"]
        except Exception as e:
            results["errors"].append(f"error validating {file_path}: {e}")
            results["invalid_files"].append({
                "path": file_path,
                "error": str(e),
            })

    return results


def merge_comic_files(
    file_paths: list[str],
    output_path: str,
    task_id: str,
    preserve_metadata: bool = True,
    zip_formats: set[str] | None = None,
    progress_callback: Callable[[MergeProgressEvent], None] | None = None,
) -> MergeResult:
    """Merge multiple comic files (CBZ and ZIP) into a single CBZ.

    Args:
        file_paths: List of comic file paths to merge.
        output_path: Output file path for the merged CBZ.
        task_id: Unique identifier for this merge task.
        preserve_metadata: Whether to include ComicInfo.xml in output.
        zip_formats: Image formats to extract from ZIP files.
        progress_callback: Optional callback for progress events.

    Returns:
        MergeResult with success status, output path, and stats.
    """
    if zip_formats is None:
        zip_formats = {"jpg"}

    # Validate inputs
    validation = validate_comic_files(file_paths)
    if validation["invalid_files"]:
        errors = [f["error"] for f in validation["invalid_files"]]
        return MergeResult(
            success=False,
            output_path=None,
            errors=errors,
        )

    result = MergeResult(
        success=False,
        output_path=output_path,
        merged_files=[],
        errors=[],
    )

    work_dir: str | None = None

    try:
        work_dir = tempfile.mkdtemp(prefix="comicmanager_merge_")
        page_number = 1
        merged_info: list[dict[str, Any]] = []

        _report_progress(
            MergeProgressEvent(
                task_id=task_id,
                stage="validating",
                current_file=None,
                current_index=0,
                total_files=len(file_paths),
                message="Starting merge...",
            ),
            progress_callback,
        )

        for i, file_path in enumerate(file_paths):
            try:
                file_type = get_file_type(file_path)

                _report_progress(
                    MergeProgressEvent(
                        task_id=task_id,
                        stage="extracting",
                        current_file=Path(file_path).name,
                        current_index=i + 1,
                        total_files=len(file_paths),
                        message=f"Extracting file {i + 1}/{len(file_paths)}",
                    ),
                    progress_callback,
                )

                if file_type == "CBZ":
                    temp_extract_dir = tempfile.mkdtemp(prefix="comicmanager_extract_")

                    with zipfile.ZipFile(file_path, "r") as zf:
                        zf.extractall(temp_extract_dir)

                    info = extract_comic_info(file_path)
                    image_files = info["image_files"]

                    pages_in_file = 0
                    for img_file in image_files:
                        src_path = Path(temp_extract_dir) / img_file
                        if src_path.exists():
                            ext = Path(img_file).suffix
                            new_name = f"{page_number:04d}{ext}"
                            dst_path = Path(work_dir) / new_name
                            shutil.copy2(src_path, dst_path)
                            page_number += 1
                            pages_in_file += 1

                    shutil.rmtree(temp_extract_dir, ignore_errors=True)

                    merged_info.append({
                        "path": file_path,
                        "name": Path(file_path).name,
                        "type": "CBZ",
                        "pages": pages_in_file,
                    })

                elif file_type == "ZIP":
                    _report_progress(
                        MergeProgressEvent(
                            task_id=task_id,
                            stage="extracting",
                            current_file=Path(file_path).name,
                            current_index=i + 1,
                            total_files=len(file_paths),
                            current_page=0,
                            total_pages=0,
                            message=f"Extracting ZIP: {Path(file_path).name}",
                        ),
                        progress_callback,
                    )

                    chapter_prefix = f"ch{i + 1}"
                    extract_result = extract_images(
                        file_path,
                        work_dir,
                        zip_formats,
                        chapter_prefix,
                    )

                    if not extract_result["success"]:
                        result.errors.append(
                            f"failed to extract from ZIP {file_path}: {extract_result.get('error', 'unknown')}"
                        )
                        continue

                    page_number += extract_result["total_extracted"]

                    merged_info.append({
                        "path": file_path,
                        "name": Path(file_path).name,
                        "type": "ZIP",
                        "pages": extract_result["total_extracted"],
                    })

            except Exception as e:
                result.errors.append(f"error processing {file_path}: {e}")
                continue

        # Collect all images from work_dir
        _report_progress(
            MergeProgressEvent(
                task_id=task_id,
                stage="writing",
                current_file=None,
                current_index=len(file_paths),
                total_files=len(file_paths),
                message="Writing output CBZ...",
            ),
            progress_callback,
        )

        output_images = sorted(
            p
            for p in Path(work_dir).glob("*")
            if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")
        )

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for img_path in output_images:
                zf.write(img_path, img_path.name)

            if preserve_metadata and merged_info:
                comic_info_xml = _create_merged_comic_info(merged_info)
                zf.writestr("ComicInfo.xml", comic_info_xml)

        from src.models.files import MergedFileInfo
        result = MergeResult(
            success=True,
            output_path=output_path,
            total_pages=len(output_images),
            merged_files=[
                MergedFileInfo(path=info["path"], name=info["name"], type=info["type"], pages=info["pages"])
                for info in merged_info
            ],
            errors=result.errors,
        )

        _report_progress(
            MergeProgressEvent(
                task_id=task_id,
                stage="done",
                current_file=None,
                current_index=len(file_paths),
                total_files=len(file_paths),
                total_pages=result.total_pages,
                message="Merge complete",
            ),
            progress_callback,
        )

    except Exception as e:
        result.errors.append(f"merge error: {e}")
        _report_progress(
            MergeProgressEvent(
                task_id=task_id,
                stage="error",
                current_file=None,
                current_index=0,
                total_files=0,
                message=str(e),
            ),
            progress_callback,
        )

    finally:
        if work_dir:
            shutil.rmtree(work_dir, ignore_errors=True)

    return result


def _create_merged_comic_info(merged_info: list[dict[str, Any]]) -> str:
    """Create a merged ComicInfo.xml content string."""
    comic_info = ET.Element("ComicInfo")
    comic_info.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    comic_info.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

    title = ET.SubElement(comic_info, "Title")
    title.text = "Merged Comic"

    summary = ET.SubElement(comic_info, "Summary")
    summary.text = f"Merged from {len(merged_info)} files"

    for i, info in enumerate(merged_info):
        file_elem = ET.SubElement(comic_info, f"SourceFile{i + 1}")
        file_elem.text = info["name"]

    return ET.tostring(comic_info, encoding="unicode", xml_declaration=True)
