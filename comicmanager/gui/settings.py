"""
设置窗口
应用程序设置和配置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, Callable, Optional

from ..core.config import Config


class SettingsWindow:
    """设置窗口类"""

    def __init__(self, parent, config: Config):
        self.parent = parent
        self.config = config
        self.window = None
        self.settings_changed = False
        self.settings_changed_callback: Optional[Callable] = None

        self._create_window()

    def _create_window(self):
        """创建设置窗口"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("设置")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        # 设置为模态窗口
        self.window.transient(self.parent)
        self.window.grab_set()

        # 设置窗口在父窗口中心
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

        self._setup_ui()

    def _setup_ui(self):
        """设置用户界面"""
        # 创建Notebook用于分页设置
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        # 常规设置页面
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="常规")
        self._setup_general_tab(general_frame)

        # 外观设置页面
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="外观")
        self._setup_appearance_tab(appearance_frame)

        # 高级设置页面
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="高级")
        self._setup_advanced_tab(advanced_frame)

        # 按钮区域
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="确定", command=self._apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self._close_window).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="重置", command=self._reset_settings).pack(side=tk.LEFT)

    def _setup_general_tab(self, parent):
        """设置常规选项页面"""
        # 默认输出目录
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(dir_frame, text="默认输出目录:").pack(anchor=tk.W)

        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=(5, 0))

        self.default_output_dir_var = tk.StringVar(
            value=self.config.get('last_output_dir', str(Path.home()))
        )
        ttk.Entry(dir_entry_frame, textvariable=self.default_output_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(dir_entry_frame, text="浏览...", command=self._browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # 其他常规选项
        options_frame = ttk.LabelFrame(parent, text="其他选项")
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.remember_files_var = tk.BooleanVar(value=self.config.get('remember_files', True))
        ttk.Checkbutton(options_frame, text="记住最近使用的文件",
                       variable=self.remember_files_var).pack(anchor=tk.W, padx=5, pady=2)

        self.backup_original_var = tk.BooleanVar(value=self.config.get('backup_original', False))
        ttk.Checkbutton(options_frame, text="合并前备份原始文件",
                       variable=self.backup_original_var).pack(anchor=tk.W, padx=5, pady=2)

        self.auto_increment_var = tk.BooleanVar(value=self.config.get('auto_increment', True))
        ttk.Checkbutton(options_frame, text="自动递增文件名避免重复",
                       variable=self.auto_increment_var).pack(anchor=tk.W, padx=5, pady=2)

    def _setup_appearance_tab(self, parent):
        """设置外观选项页面"""
        # 主题选择
        theme_frame = ttk.Frame(parent)
        theme_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(theme_frame, text="界面主题:").pack(anchor=tk.W)

        self.theme_var = tk.StringVar(value=self.config.get('theme', 'default'))
        themes = ['default', 'clam', 'alt', 'classic']
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=themes, state='readonly')
        theme_combo.pack(fill=tk.X, pady=(5, 0))
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)

        # 字体大小设置
        font_frame = ttk.LabelFrame(parent, text="字体设置")
        font_frame.pack(fill=tk.X, padx=10, pady=10)

        size_frame = ttk.Frame(font_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(size_frame, text="字体大小:").pack(side=tk.LEFT)
        self.font_size_var = tk.StringVar(value=self.config.get('font_size', '10'))
        font_size_spin = ttk.Spinbox(size_frame, from_=8, to=20, width=10,
                                     textvariable=self.font_size_var)
        font_size_spin.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(size_frame, text="pt").pack(side=tk.LEFT, padx=(2, 0))

    def _setup_advanced_tab(self, parent):
        """设置高级选项页面"""
        # 性能设置
        performance_frame = ttk.LabelFrame(parent, text="性能设置")
        performance_frame.pack(fill=tk.X, padx=10, pady=10)

        self.chunk_size_var = tk.StringVar(value=self.config.get('chunk_size', '64'))
        chunk_frame = ttk.Frame(performance_frame)
        chunk_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(chunk_frame, text="文件读取块大小 (MB):").pack(side=tk.LEFT)
        ttk.Spinbox(chunk_frame, from_=1, to=1024, width=10,
                   textvariable=self.chunk_size_var).pack(side=tk.LEFT, padx=(5, 0))

        # 内存设置
        memory_frame = ttk.Frame(performance_frame)
        memory_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(memory_frame, text="最大内存使用 (MB):").pack(side=tk.LEFT)
        self.max_memory_var = tk.StringVar(value=self.config.get('max_memory', '512'))
        ttk.Spinbox(memory_frame, from_=64, to=4096, width=10,
                   textvariable=self.max_memory_var).pack(side=tk.LEFT, padx=(5, 0))

        # 临时文件设置
        temp_frame = ttk.LabelFrame(parent, text="临时文件设置")
        temp_frame.pack(fill=tk.X, padx=10, pady=10)

        self.cleanup_temp_var = tk.BooleanVar(value=self.config.get('cleanup_temp', True))
        ttk.Checkbutton(temp_frame, text="程序退出时自动清理临时文件",
                       variable=self.cleanup_temp_var).pack(anchor=tk.W, padx=5, pady=2)

        temp_dir_frame = ttk.Frame(temp_frame)
        temp_dir_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(temp_dir_frame, text="临时文件目录:").pack(anchor=tk.W)

        temp_entry_frame = ttk.Frame(temp_dir_frame)
        temp_entry_frame.pack(fill=tk.X, pady=(5, 0))

        self.temp_dir_var = tk.StringVar(value=self.config.get('temp_dir', ''))
        ttk.Entry(temp_entry_frame, textvariable=self.temp_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(temp_entry_frame, text="浏览...", command=self._browse_temp_dir).pack(side=tk.RIGHT, padx=(5, 0))

    def _browse_output_dir(self):
        """浏览默认输出目录"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(
            title="选择默认输出目录",
            initialdir=self.default_output_dir_var.get()
        )
        if directory:
            self.default_output_dir_var.set(directory)

    def _browse_temp_dir(self):
        """浏览临时文件目录"""
        from tkinter import filedialog
        initial_dir = self.temp_dir_var.get() or str(Path.home())
        directory = filedialog.askdirectory(
            title="选择临时文件目录",
            initialdir=initial_dir
        )
        if directory:
            self.temp_dir_var.set(directory)

    def _on_theme_change(self, event=None):
        """主题改变时的处理"""
        # 这里可以添加主题预览功能
        pass

    def _apply_settings(self):
        """应用设置"""
        try:
            # 常规设置
            self.config.set('last_output_dir', self.default_output_dir_var.get())
            self.config.set('remember_files', self.remember_files_var.get())
            self.config.set('backup_original', self.backup_original_var.get())
            self.config.set('auto_increment', self.auto_increment_var.get())

            # 外观设置
            self.config.set('theme', self.theme_var.get())
            self.config.set('font_size', self.font_size_var.get())

            # 高级设置
            self.config.set('chunk_size', self.chunk_size_var.get())
            self.config.set('max_memory', self.max_memory_var.get())
            self.config.set('cleanup_temp', self.cleanup_temp_var.get())
            if self.temp_dir_var.get():
                self.config.set('temp_dir', self.temp_dir_var.get())

            self.settings_changed = True

            # 如果有设置变更回调，调用它
            if self.settings_changed_callback:
                self.settings_changed_callback()

            messagebox.showinfo("设置", "设置已保存")
            self._close_window()

        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def _reset_settings(self):
        """重置设置到默认值"""
        if messagebox.askyesno("重置设置", "确定要重置所有设置到默认值吗？"):
            try:
                # 重置到默认值
                self.default_output_dir_var.set(str(Path.home()))
                self.remember_files_var.set(True)
                self.backup_original_var.set(False)
                self.auto_increment_var.set(True)
                self.theme_var.set('default')
                self.font_size_var.set('10')
                self.chunk_size_var.set('64')
                self.max_memory_var.set('512')
                self.cleanup_temp_var.set(True)
                self.temp_dir_var.set('')

                messagebox.showinfo("重置设置", "设置已重置到默认值")

            except Exception as e:
                messagebox.showerror("错误", f"重置设置失败: {str(e)}")

    def _close_window(self):
        """关闭设置窗口"""
        self.window.destroy()

    def set_settings_changed_callback(self, callback: Callable[[], None]) -> None:
        """设置设置变更回调函数"""
        self.settings_changed_callback = callback

    def show(self):
        """显示设置窗口"""
        self.window.wait_window()