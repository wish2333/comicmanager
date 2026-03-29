"""Background merge task management with async progress bridging.

Uses asyncio.Queue to bridge sync merge logic into async SSE streams.
"""

from __future__ import annotations

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from src.models.progress import MergeProgressEvent
from src.services.merger import merge_comic_files


class MergeTaskManager:
    """Manages background merge tasks and their progress queues."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[MergeProgressEvent]] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._executor = ThreadPoolExecutor(max_workers=2)

    def _generate_task_id(self) -> str:
        return str(uuid.uuid4())[:8]

    def _progress_callback(
        self,
        task_id: str,
        queue: asyncio.Queue[MergeProgressEvent],
        event: MergeProgressEvent,
    ) -> None:
        """Callback from sync merge that puts events onto the async queue."""
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(queue.put_nowait, event)
        except RuntimeError:
            pass

    async def start_merge(
        self,
        file_paths: list[str],
        output_path: str,
        preserve_metadata: bool = True,
        zip_formats: set[str] | None = None,
    ) -> str:
        """Start a merge task in a background thread. Returns task_id."""
        task_id = self._generate_task_id()
        queue: asyncio.Queue[MergeProgressEvent] = asyncio.Queue()
        self._queues[task_id] = queue

        callback = lambda event, tid=task_id, q=queue: self._progress_callback(tid, q, event)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: merge_comic_files(
                file_paths=file_paths,
                output_path=output_path,
                task_id=task_id,
                preserve_metadata=preserve_metadata,
                zip_formats=zip_formats,
                progress_callback=callback,
            ),
        )

        # Wait briefly for the result to be available
        return task_id

    async def run_merge(
        self,
        file_paths: list[str],
        output_path: str,
        preserve_metadata: bool = True,
        zip_formats: set[str] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Run merge synchronously (in executor), return (task_id, result)."""
        task_id = self._generate_task_id()
        queue: asyncio.Queue[MergeProgressEvent] = asyncio.Queue()
        self._queues[task_id] = queue

        callback = lambda event, tid=task_id, q=queue: self._progress_callback(tid, q, event)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            lambda: merge_comic_files(
                file_paths=file_paths,
                output_path=output_path,
                task_id=task_id,
                preserve_metadata=preserve_metadata,
                zip_formats=zip_formats,
                progress_callback=callback,
            ),
        )

        result_dict = result.model_dump()
        self._results[task_id] = result_dict
        return task_id, result_dict

    def get_progress_queue(self, task_id: str) -> asyncio.Queue[MergeProgressEvent] | None:
        """Get the progress queue for a task."""
        return self._queues.get(task_id)

    def get_result(self, task_id: str) -> dict[str, Any] | None:
        """Get the result of a completed task."""
        return self._results.get(task_id)

    def cleanup_task(self, task_id: str) -> None:
        """Remove a task's queue and result."""
        self._queues.pop(task_id, None)
        self._results.pop(task_id, None)


merge_task_manager = MergeTaskManager()
