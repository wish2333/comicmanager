"""
拖拽处理器
处理文件拖拽相关功能
"""

import tkinter as tk
from pathlib import Path
from typing import List, Optional, Callable
import os

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False


class DragDropHandler:
    """拖拽处理器类"""

    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.drop_callback: Optional[Callable[[List[str]], None]] = None
        self.drag_drop_enabled = False

        if DRAG_DROP_AVAILABLE:
            self._enable_drag_drop()

    def _enable_drag_drop(self):
        """启用拖拽功能"""
        try:
            self.parent_widget.drag_dest_register(DND_FILES)
            self.parent_widget.dnd_bind('<<Drop>>', self._on_drop)
            self.parent_widget.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.parent_widget.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            self.drag_drop_enabled = True
        except Exception as e:
            print(f"启用拖拽功能失败: {e}")
            self.drag_drop_enabled = False

    def set_drop_callback(self, callback: Callable[[List[str]], None]) -> None:
        """设置拖拽放下回调函数"""
        self.drop_callback = callback

    def _on_drop(self, event):
        """处理拖拽放下事件"""
        if self.drop_callback:
            try:
                # 解析文件路径
                file_paths = []
                if hasattr(event, 'data'):
                    # Windows系统下，文件路径可能包含换行符
                    paths = event.data.split('\n')
                    file_paths = [Path(p.strip()).as_posix() for p in paths if p.strip()]

                # 过滤CBZ文件
                cbz_files = [f for f in file_paths if f.lower().endswith('.cbz') and os.path.exists(f)]

                if cbz_files:
                    self.drop_callback(cbz_files)

            except Exception as e:
                print(f"处理拖拽文件时出错: {e}")

    def _on_drag_enter(self, event):
        """拖拽进入事件"""
        # 可以在这里添加视觉反馈
        pass

    def _on_drag_leave(self, event):
        """拖拽离开事件"""
        # 可以在这里移除视觉反馈
        pass

    def is_available(self) -> bool:
        """检查拖拽功能是否可用"""
        return DRAG_DROP_AVAILABLE and self.drag_drop_enabled