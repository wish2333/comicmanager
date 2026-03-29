"""In-memory application state for file queue and merge tasks."""

from __future__ import annotations

import threading
from typing import Any

from src.models.files import QueuedFile


class AppState:
    """Thread-safe in-memory state holder."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._files: list[QueuedFile] = []
        self._active_task_id: str | None = None

    @property
    def files(self) -> list[QueuedFile]:
        with self._lock:
            return list(self._files)

    @property
    def active_task_id(self) -> str | None:
        with self._lock:
            return self._active_task_id

    def set_files(self, files: list[QueuedFile]) -> None:
        with self._lock:
            self._files = list(files)

    def add_files(self, new_files: list[QueuedFile]) -> list[QueuedFile]:
        with self._lock:
            self._files = [*self._files, *new_files]
            return list(self._files)

    def remove_by_indices(self, indices: list[int]) -> list[QueuedFile]:
        with self._lock:
            keep = [f for i, f in enumerate(self._files) if i not in indices]
            self._files = keep
            return list(self._files)

    def clear_files(self) -> list[QueuedFile]:
        with self._lock:
            self._files = []
            return []

    def reorder(self, from_index: int, to_index: int) -> list[QueuedFile]:
        with self._lock:
            files = list(self._files)
            if 0 <= from_index < len(files) and 0 <= to_index < len(files):
                item = files.pop(from_index)
                files.insert(to_index, item)
                self._files = files
            return list(self._files)

    def sort_by_name(self, reverse: bool = False) -> list[QueuedFile]:
        with self._lock:
            self._files = sorted(
                self._files,
                key=lambda f: f.name.lower(),
                reverse=reverse,
            )
            return list(self._files)

    def set_active_task_id(self, task_id: str | None) -> None:
        with self._lock:
            self._active_task_id = task_id


app_state = AppState()
