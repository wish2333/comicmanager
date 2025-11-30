"""
图片格式选择器组件
用于选择要从ZIP文件中提取的图片格式
"""

import tkinter as tk
from tkinter import ttk
from typing import Set, List, Optional, Callable
from ..core.zip_extractor import ZIPExtractor


class FormatSelector:
    """图片格式选择器"""

    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.format_vars = {}
        self.selected_formats = {'jpg'}  # 默认格式
        self.callback: Optional[Callable[[Set[str]], None]] = None

        self._setup_ui()

    def _setup_ui(self):
        """设置用户界面"""
        # 主框架
        self.main_frame = ttk.LabelFrame(self.parent, text="ZIP文件图片格式")
        self.main_frame.pack(fill=tk.X, padx=5, pady=5)

        # 提示标签
        hint_label = ttk.Label(self.main_frame,
                             text="选择要从ZIP文件中提取的图片格式:")
        hint_label.pack(anchor=tk.W, padx=5, pady=(5, 0))

        # 复选框框架
        checkbox_frame = ttk.Frame(self.main_frame)
        checkbox_frame.pack(fill=tk.X, padx=5, pady=5)

        # 获取支持的格式
        extractor = ZIPExtractor()
        supported_formats = extractor.get_supported_formats()

        # 创建复选框
        for i, format_name in enumerate(supported_formats):
            var = tk.BooleanVar()
            if format_name in self.selected_formats:
                var.set(True)

            checkbox = ttk.Checkbutton(
                checkbox_frame,
                text=format_name.upper(),
                variable=var,
                command=self._on_format_changed
            )
            checkbox.grid(row=0, column=i, padx=(0, 10), sticky=tk.W)
            self.format_vars[format_name] = var

        # 快速选择按钮
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Button(
            button_frame,
            text="全选",
            command=self._select_all
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="仅JPG",
            command=self._select_jpg_only
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="仅WEBP",
            command=self._select_webp_only
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="清空",
            command=self._clear_all
        ).pack(side=tk.LEFT)

    def _on_format_changed(self):
        """处理格式选择变化"""
        # 获取选中的格式
        self.selected_formats = set()
        for format_name, var in self.format_vars.items():
            if var.get():
                self.selected_formats.add(format_name)

        # 如果没有选择任何格式，默认选择JPG
        if not self.selected_formats:
            self.format_vars['jpg'].set(True)
            self.selected_formats.add('jpg')

        # 调用回调函数
        if self.callback:
            self.callback(self.selected_formats)

    def _select_all(self):
        """选择所有格式"""
        for var in self.format_vars.values():
            var.set(True)
        self._on_format_changed()

    def _select_jpg_only(self):
        """仅选择JPG格式"""
        for format_name, var in self.format_vars.items():
            var.set(format_name == 'jpg' or format_name == 'jpeg')
        self._on_format_changed()

    def _select_webp_only(self):
        """仅选择WEBP格式"""
        for format_name, var in self.format_vars.items():
            var.set(format_name == 'webp')
        self._on_format_changed()

    def _clear_all(self):
        """清空所有选择"""
        for var in self.format_vars.values():
            var.set(False)
        self._on_format_changed()

    def get_selected_formats(self) -> Set[str]:
        """获取选中的格式"""
        return self.selected_formats.copy()

    def set_selected_formats(self, formats: Set[str]):
        """设置选中的格式"""
        self.selected_formats = set(formats) if formats else {'jpg'}

        # 更新复选框状态
        for format_name, var in self.format_vars.items():
            var.set(format_name in self.selected_formats)

    def set_callback(self, callback: Callable[[Set[str]], None]):
        """设置选择变化回调函数"""
        self.callback = callback

    def enable(self):
        """启用选择器"""
        for child in self.main_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton) or isinstance(child, ttk.Button):
                child.config(state='normal')

    def disable(self):
        """禁用选择器"""
        for child in self.main_frame.winfo_children():
            if isinstance(child, ttk.Checkbutton) or isinstance(child, ttk.Button):
                child.config(state='disabled')

    def pack(self, **kwargs):
        """包装pack方法"""
        self.main_frame.pack(**kwargs)

    def grid(self, **kwargs):
        """包装grid方法"""
        self.main_frame.grid(**kwargs)