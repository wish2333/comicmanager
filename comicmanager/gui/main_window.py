"""
主窗口界面
应用程序的主要图形用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import List, Optional

from ..core.cbz_merger import CBZMerger, MergeProgress
from ..core.config import Config
from ..core.file_utils import FileUtils
from .file_list_widget import FileListWidget

# 尝试导入tkinterdnd2的TkinterDnD包装器
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TKINTERDND_AVAILABLE = True
except ImportError:
    TKINTERDND_AVAILABLE = False
    DND_FILES = None
except Exception:
    TKINTERDND_AVAILABLE = False
    DND_FILES = None


class MainWindow:
    """主窗口类"""

    def __init__(self):
        # 使用TkinterDnD包装器（如果可用）
        if TKINTERDND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.config = Config()
        self.merger = CBZMerger()
        self.file_list_widget = None

        self._setup_window()
        self._setup_menu()
        self._setup_ui()
        self._setup_drag_drop()
        self._setup_bindings()

    def _setup_window(self):
        """设置窗口属性"""
        self.root.title("ComicManager - CBZ文件合并工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass

    def _setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件(F)", menu=file_menu)
        file_menu.add_command(label="添加文件...", command=self._add_files, accelerator="Ctrl+O")
        file_menu.add_command(label="清空列表", command=self._clear_list)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._quit, accelerator="Ctrl+Q")

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑(E)", menu=edit_menu)
        edit_menu.add_command(label="全选", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="删除选中", command=self._remove_selected, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="上移", command=self._move_up, accelerator="Ctrl+Up")
        edit_menu.add_command(label="下移", command=self._move_down, accelerator="Ctrl+Down")
        edit_menu.add_command(label="移至顶部", command=self._move_to_top, accelerator="Ctrl+Home")
        edit_menu.add_command(label="移至底部", command=self._move_to_bottom, accelerator="Ctrl+End")

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助(H)", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 文件列表区域
        file_frame = ttk.LabelFrame(main_frame, text="CBZ文件列表")
        file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 工具栏
        toolbar_frame = ttk.Frame(file_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar_frame, text="添加文件", command=self._add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="删除选中", command=self._remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="清空列表", command=self._clear_list).pack(side=tk.LEFT, padx=(0, 10))

        # 分隔符
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 排序按钮
        ttk.Button(toolbar_frame, text="上移", command=self._move_up).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar_frame, text="下移", command=self._move_down).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar_frame, text="置顶", command=self._move_to_top).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar_frame, text="置底", command=self._move_to_bottom).pack(side=tk.LEFT, padx=(0, 5))

        # 文件列表组件
        self.file_list_widget = FileListWidget(file_frame)
        self.file_list_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # 设置选择回调
        self.file_list_widget.set_selection_callback(self._on_selection_changed)

        # 输出设置区域
        output_frame = ttk.LabelFrame(main_frame, text="输出设置")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        # 输出文件名
        name_frame = ttk.Frame(output_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(name_frame, text="输出文件名:").pack(side=tk.LEFT)
        self.output_filename_var = tk.StringVar(value="merged_comic.cbz")
        self.output_filename_entry = ttk.Entry(name_frame, textvariable=self.output_filename_var)
        self.output_filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        ttk.Button(name_frame, text="浏览...", command=self._browse_output).pack(side=tk.LEFT, padx=(0, 5))

        # 输出目录
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(dir_frame, text="保存目录:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=self.config.get('last_output_dir', str(Path.home())))
        self.output_dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir_var)
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        ttk.Button(dir_frame, text="选择...", command=self._browse_output_dir).pack(side=tk.LEFT)

        # 合并选项
        options_frame = ttk.Frame(output_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.preserve_metadata_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保留原始元数据",
                       variable=self.preserve_metadata_var).pack(side=tk.LEFT)

        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧统计信息
        self.stats_label = ttk.Label(button_frame, text="文件: 0 | 总页数: 0")
        self.stats_label.pack(side=tk.LEFT)

        # 右侧操作按钮
        ttk.Button(button_frame, text="开始合并", command=self._start_merge,
                  style="Accent.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="退出", command=self._quit).pack(side=tk.RIGHT)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.pack(fill=tk.X)

    def _setup_drag_drop(self):
        """设置文件拖拽功能"""
        if TKINTERDND_AVAILABLE:
            try:
                # 设置整个窗口为拖拽目标
                self.root.drop_target_register(DND_FILES)
                self.root.dnd_bind('<<Drop>>', self._on_files_dropped)
                print("主窗口拖拽功能已启用")
            except Exception as e:
                print(f"拖拽功能设置失败: {e}")

    def _on_files_dropped(self, event):
        """处理文件拖拽事件"""
        try:
            # 解析文件路径
            import os
            import re
            if hasattr(event, 'data'):
                # Windows系统处理 - 获取原始数据
                raw_data = event.data
                print(f"拖拽原始数据: {repr(raw_data)}")  # 调试信息

                # 智能解析拖拽数据
                file_paths = self._parse_drag_drop_data(raw_data)
                print(f"解析出 {len(file_paths)} 个文件路径")

            else:
                print("拖拽事件没有data属性")
                return

            # 过滤CBZ文件
            cbz_files = []
            for file_path in file_paths:
                print(f"验证文件: {file_path}")  # 调试信息
                print(f"  文件存在: {os.path.exists(file_path)}")
                print(f"  是文件: {os.path.isfile(file_path) if os.path.exists(file_path) else 'N/A'}")
                print(f"  扩展名: {os.path.splitext(file_path)[1].lower()}")

                # 使用与按钮添加相同的验证逻辑
                if (file_path.lower().endswith('.cbz') and
                    os.path.exists(file_path) and
                    os.path.isfile(file_path)):
                    cbz_files.append(file_path)
                    print(f"  -> 有效CBZ文件")

            print(f"找到 {len(cbz_files)} 个有效CBZ文件")

            if cbz_files:
                # 添加文件到列表
                self.file_list_widget.add_files(cbz_files)
                print(f"通过拖拽添加了 {len(cbz_files)} 个文件")
                self._update_stats()  # 更新统计信息
            else:
                print("没有找到有效的CBZ文件")

        except Exception as e:
            print(f"处理拖拽文件时出错: {e}")
            import traceback
            traceback.print_exc()

    def _parse_drag_drop_data(self, raw_data):
        """智能解析拖拽数据，支持多种格式"""
        import os
        import re
        from urllib.parse import unquote

        if not isinstance(raw_data, str):
            return [str(raw_data)]

        raw_data = raw_data.strip()

        # 策略1: 花括号格式 - {path1} {path2} {path3}
        if raw_data.startswith('{') and '}' in raw_data:
            print("检测到花括号格式，使用正则表达式解析...")
            # 匹配花括号内的内容，支持路径中的空格
            pattern = r'\{([^{}]+\.cbz)\}'
            matches = re.findall(pattern, raw_data, re.IGNORECASE)
            if matches:
                file_paths = [match.strip() for match in matches if match.strip()]
                print(f"花括号解析结果: {len(file_paths)} 个路径")
                for i, path in enumerate(file_paths):
                    print(f"  {i+1}. {path}")
                return self._clean_file_paths(file_paths)
            else:
                # 如果没有找到.cbz结尾的，尝试更宽泛的匹配
                pattern = r'\{([^{}]+)\}'
                matches = re.findall(pattern, raw_data)
                if matches:
                    file_paths = [match.strip() for match in matches if match.strip() and '.cbz' in match.lower()]
                    print(f"花括号宽泛解析结果: {len(file_paths)} 个路径")
                    for i, path in enumerate(file_paths):
                        print(f"  {i+1}. {path}")
                    return self._clean_file_paths(file_paths)

        # 策略2: 多行格式 - path1\npath2\npath3
        if '\n' in raw_data or '\r\n' in raw_data:
            print("检测到多行格式...")
            lines = raw_data.replace('\r\n', '\n').split('\n')
            file_paths = [line.strip() for line in lines if line.strip()]
            print(f"多行解析结果: {len(file_paths)} 个路径")
            return self._clean_file_paths(file_paths)

        # 策略3: 引号分隔格式 - "path1" "path2" "path3"
        if '"' in raw_data or "'" in raw_data:
            print("检测到引号分隔格式...")
            import shlex
            try:
                file_paths = shlex.split(raw_data)
                print(f"引号解析结果: {len(file_paths)} 个路径")
                return self._clean_file_paths(file_paths)
            except:
                print("shlex解析失败，尝试其他方法...")

        # 策略4: URI格式 - file://path1 file://path2
        if raw_data.startswith('file://'):
            print("检测到URI格式...")
            paths = raw_data.split()
            file_paths = []
            for path in paths:
                if path.startswith('file://'):
                    path = unquote(path[7:])
                file_paths.append(path)
            print(f"URI解析结果: {len(file_paths)} 个路径")
            return self._clean_file_paths(file_paths)

        # 策略5: 简单空格分割（最后尝试）
        print("使用简单空格分割...")
        # 检查是否包含驱动器字母模式（Windows路径）
        if re.search(r'[a-zA-Z]:[\\/]', raw_data):
            # Windows路径，智能分割
            parts = re.split(r'(?<=[.]cbz)\s+(?=[a-zA-Z]:|[\\/])', raw_data)
            file_paths = [part.strip() for part in parts if part.strip()]
        else:
            # 普通空格分割
            file_paths = raw_data.split()

        print(f"空格分割结果: {len(file_paths)} 个路径")
        return self._clean_file_paths(file_paths)

    def _clean_file_paths(self, file_paths):
        """清理和标准化文件路径"""
        import os
        from urllib.parse import unquote

        cleaned_paths = []

        for i, file_path in enumerate(file_paths):
            if not file_path or not file_path.strip():
                continue

            original_path = file_path
            file_path = file_path.strip()

            print(f"清理路径 {i+1}: {repr(original_path)}")

            # 移除多余的引号
            if (file_path.startswith('"') and file_path.endswith('"')) or \
               (file_path.startswith("'") and file_path.endswith("'")):
                file_path = file_path[1:-1]

            # 处理URI格式
            if file_path.startswith('file://'):
                file_path = unquote(file_path[7:])

            # 标准化路径分隔符
            file_path = os.path.normpath(file_path)

            # 验证是否看起来像文件路径
            if self._looks_like_file_path(file_path):
                cleaned_paths.append(file_path)
                print(f"  -> 清理后: {file_path}")
            else:
                print(f"  -> 跳过（不像有效文件路径）: {file_path}")

        return cleaned_paths

    def _looks_like_file_path(self, path):
        """检查字符串是否看起来像有效的文件路径"""
        import os
        import re

        # 检查是否包含驱动器字母（Windows）或绝对路径标记
        if not (re.match(r'^[a-zA-Z]:', path) or path.startswith('/') or path.startswith('\\')):
            return False

        # 检查是否包含文件名（有扩展名或者最后部分不包含路径分隔符）
        if '.' not in os.path.basename(path) and len(os.path.basename(path)) > 0:
            # 没有扩展名但有文件名，可能是目录
            return not os.path.isdir(path) if os.path.exists(path) else True

        return True

    def _setup_bindings(self):
        """设置键盘快捷键"""
        self.root.bind('<Control-o>', lambda e: self._add_files())
        self.root.bind('<Control-q>', lambda e: self._quit())
        self.root.bind('<Control-a>', lambda e: self._select_all())
        self.root.bind('<Delete>', lambda e: self._remove_selected())

    def _add_files(self):
        """添加CBZ文件"""
        last_dir = self.config.get('last_input_dir', str(Path.home()))
        file_paths = filedialog.askopenfilenames(
            title="选择CBZ文件",
            initialdir=last_dir,
            filetypes=[("CBZ文件", "*.cbz"), ("ZIP文件", "*.zip"), ("所有文件", "*.*")]
        )

        if file_paths:
            # 保存最后使用的目录
            self.config.set('last_input_dir', str(Path(file_paths[0]).parent))

            # 添加文件到列表
            self.file_list_widget.add_files(list(file_paths))

            # 更新统计信息
            self._update_stats()

            # 更新输出文件名建议
            if len(file_paths) == 1:
                self.output_filename_var.set(f"merged_{Path(file_paths[0]).stem}.cbz")
            else:
                parent_name = Path(file_paths[0]).parent.name
                self.output_filename_var.set(f"merged_{parent_name}.cbz")

    def _remove_selected(self):
        """删除选中的文件"""
        self.file_list_widget.remove_selected()
        self._update_stats()

    def _clear_list(self):
        """清空文件列表"""
        self.file_list_widget.clear_all()
        self._update_stats()

    def _select_all(self):
        """选择所有文件"""
        if hasattr(self.file_list_widget, 'tree'):
            self.file_list_widget.tree.selection_set(self.file_list_widget.tree.get_children())

    def _move_up(self):
        """向上移动选中的文件"""
        self.file_list_widget.move_selected_up()

    def _move_down(self):
        """向下移动选中的文件"""
        self.file_list_widget.move_selected_down()

    def _move_to_top(self):
        """移动选中的文件到顶部"""
        self.file_list_widget.move_selected_to_top()

    def _move_to_bottom(self):
        """移动选中的文件到底部"""
        self.file_list_widget.move_selected_to_bottom()

    def _browse_output(self):
        """浏览输出文件位置"""
        output_dir = self.output_dir_var.get()
        if not output_dir:
            output_dir = str(Path.home())

        file_path = filedialog.asksaveasfilename(
            title="选择输出文件位置",
            initialdir=output_dir,
            initialfile=self.output_filename_var.get(),
            filetypes=[("CBZ文件", "*.cbz"), ("所有文件", "*.*")]
        )

        if file_path:
            self.output_filename_var.set(Path(file_path).name)
            self.output_dir_var.set(str(Path(file_path).parent))
            self.config.set('last_output_dir', str(Path(file_path).parent))

    def _browse_output_dir(self):
        """选择输出目录"""
        output_dir = self.output_dir_var.get()
        if not output_dir:
            output_dir = str(Path.home())

        directory = filedialog.askdirectory(title="选择输出目录", initialdir=output_dir)

        if directory:
            self.output_dir_var.set(directory)
            self.config.set('last_output_dir', directory)

    def _start_merge(self):
        """开始合并操作"""
        file_paths = self.file_list_widget.get_file_paths()

        if not file_paths:
            messagebox.showwarning("警告", "请先添加要合并的CBZ文件")
            return

        if len(file_paths) == 1:
            messagebox.showinfo("提示", "只有一个文件，无需合并")
            return

        # 获取输出路径
        output_filename = self.output_filename_var.get().strip()
        if not output_filename:
            messagebox.showwarning("警告", "请指定输出文件名")
            return

        if not output_filename.lower().endswith('.cbz'):
            output_filename += '.cbz'

        output_dir = self.output_dir_var.get()
        output_path = str(Path(output_dir) / output_filename)

        # 验证输出路径
        valid, error_msg = FileUtils.validate_output_path(output_path)
        if not valid:
            messagebox.showerror("错误", error_msg)
            return

        # 禁用操作按钮
        self._set_ui_state(False)

        # 在后台线程执行合并
        def merge_thread():
            # 设置进度回调
            self.merger.set_progress_callback(self._on_merge_progress)

            # 执行合并
            result = self.merger.merge_cbz_files(
                file_paths,
                output_path,
                self.preserve_metadata_var.get()
            )

            # 在主线程显示结果
            self.root.after(0, self._on_merge_complete, result)

        thread = threading.Thread(target=merge_thread, daemon=True)
        thread.start()

        self.status_label.config(text="正在合并文件...")

    def _on_merge_progress(self, progress: MergeProgress):
        """处理合并进度更新"""
        self.root.after(0, lambda: self._update_progress(progress))

    def _update_progress(self, progress: MergeProgress):
        """更新进度显示"""
        total_files = len(self.file_list_widget.get_file_paths())
        current_progress = (progress.current_progress / total_files) * 100
        self.progress_var.set(current_progress)
        self.status_label.config(text=f"{progress.message} ({progress.current_progress}/{total_files})")

    def _on_merge_complete(self, result):
        """处理合并完成"""
        # 重置进度条
        self.progress_var.set(0)

        # 恢复UI状态
        self._set_ui_state(True)

        if result['success']:
            messagebox.showinfo("成功",
                f"文件合并完成！\n\n"
                f"输出文件: {result['output_path']}\n"
                f"总页数: {result['total_pages']}\n"
                f"合并文件数: {len(result['merged_files'])}")

            self.status_label.config(text="合并完成")
        else:
            error_msg = result.get('error', '未知错误')
            messagebox.showerror("错误", f"合并失败: {error_msg}")
            self.status_label.config(text=f"合并失败: {error_msg}")

    def _set_ui_state(self, enabled: bool):
        """设置UI控件的启用/禁用状态"""
        state = 'normal' if enabled else 'disabled'
        # 这里可以添加更多控件的启用/禁用逻辑
        # for widget in self.root.winfo_children():
        #     try:
        #         widget.config(state=state)
        #     except:
        #         pass

    def _on_selection_changed(self):
        """处理选择变化"""
        self._update_stats()

    def _update_stats(self):
        """更新统计信息"""
        file_paths = self.file_list_widget.get_file_paths()
        file_count = len(file_paths)

        # 计算总页数
        total_pages = 0
        for file_path in file_paths:
            info = FileUtils.extract_cbz_info(file_path)
            if 'error' not in info:
                total_pages += info['page_count']

        self.stats_label.config(text=f"文件: {file_count} | 总页数: {total_pages}")

    def _show_help(self):
        """显示帮助信息"""
        help_text = """ComicManager 使用说明

1. 添加文件:
   • 点击"添加文件"按钮或使用 Ctrl+O
   • 支持选择多个CBZ文件

2. 调整顺序:
   • 使用拖拽方式调整文件顺序
   • 选中文件后使用上移/下移按钮
   • 支持Ctrl+点击多选，Shift+点击范围选择

3. 键盘快捷键:
   • Ctrl+O: 添加文件
   • Ctrl+A: 全选
   • Delete: 删除选中
   • Ctrl+Up/Down: 上移/下移选中项
   • Ctrl+Home/End: 移至顶部/底部

4. 合并设置:
   • 设置输出文件名和保存目录
   • 选择是否保留原始元数据

5. 开始合并:
   • 点击"开始合并"按钮执行合并操作
   • 合并过程中会显示进度信息

注意: 合并操作会按照文件列表的顺序进行，请确保顺序正确。"""

        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        """显示关于信息"""
        about_text = """ComicManager v0.1.0

一个简单易用的CBZ文件合并工具

特性:
• 支持多个CBZ文件合并
• 拖拽排序功能
• 保留原始元数据
• 进度显示

开发语言: Python
GUI框架: Tkinter

感谢使用 ComicManager！"""

        messagebox.showinfo("关于 ComicManager", about_text)

    def _quit(self):
        """退出应用程序"""
        if messagebox.askokcancel("退出", "确定要退出 ComicManager 吗？"):
            self.merger.cleanup()
            self.root.quit()
            self.root.destroy()

    def run(self):
        """运行应用程序"""
        self.root.mainloop()