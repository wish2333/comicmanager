"""
文件列表组件
支持拖拽排序的CBZ文件列表
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import os

# 导入文件工具类
try:
    from ..core.file_utils import FileUtils
except ImportError:
    # 如果导入失败，定义一个简单的替代实现
    class FileUtils:
        @staticmethod
        def get_file_size_str(file_path: str) -> str:
            try:
                size = os.path.getsize(file_path)
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except:
                return "未知"

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    DND_FILES = None
    print("警告: tkinterdnd2 未安装，拖拽功能将不可用")
except Exception as e:
    DRAG_DROP_AVAILABLE = False
    DND_FILES = None
    print(f"警告: tkinterdnd2 初始化失败，拖拽功能将不可用: {e}")

# 尝试导入ttk的拖拽增强版本
try:
    from tkinterdnd2.ttk import Treeview as DragDropTreeview
    TREEVIEW_SUPPORTS_DRAG = True
except ImportError:
    try:
        from tkinter import ttk
        Treeview = ttk.Treeview
        TREEVIEW_SUPPORTS_DRAG = False
    except ImportError:
        TREEVIEW_SUPPORTS_DRAG = False


class FileListWidget(ttk.Frame):
    """支持拖拽排序的文件列表组件"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.file_list: List[Dict[str, Any]] = []
        self.selected_indices: List[int] = []
        self.selection_callback: Optional[Callable] = None
        self.drag_start_index: Optional[int] = None
        self.drag_drop_enabled: bool = False

        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        """设置用户界面"""
        # 创建框架
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建Treeview - 使用支持拖拽的版本（如果可用）
        columns = ('name', 'size', 'pages', 'path')
        if TREEVIEW_SUPPORTS_DRAG:
            self.tree = DragDropTreeview(self.frame, columns=columns, show='tree headings', height=10)
            print("使用tkinterdnd2增强版Treeview")
        else:
            self.tree = ttk.Treeview(self.frame, columns=columns, show='tree headings', height=10)
            print("使用标准Treeview")

        # 设置列标题
        self.tree.heading('#0', text='序号')
        self.tree.heading('name', text='文件名')
        self.tree.heading('size', text='大小')
        self.tree.heading('pages', text='页数')
        self.tree.heading('path', text='路径')

        # 设置列宽
        self.tree.column('#0', width=50, minwidth=30)
        self.tree.column('name', width=200, minwidth=100)
        self.tree.column('size', width=100, minwidth=60)
        self.tree.column('pages', width=60, minwidth=40)
        self.tree.column('path', width=300, minwidth=100)

        # 添加滚动条
        v_scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # 设置拖拽支持 - 条件性启用Treeview拖拽
        self.drag_drop_enabled = DRAG_DROP_AVAILABLE
        if self.drag_drop_enabled:
            print("Treeview拖拽排序功能已启用")
        else:
            print("Treeview拖拽排序功能不可用，请使用按钮和键盘操作调整顺序")

    def _setup_bindings(self):
        """设置事件绑定"""
        # 鼠标事件
        self.tree.bind('<Button-1>', self._on_item_click)
        self.tree.bind('<Double-Button-1>', self._on_double_click)  # 双击事件
        self.tree.bind('<Control-Button-1>', self._on_ctrl_click)
        self.tree.bind('<Shift-Button-1>', self._on_shift_click)
        self.tree.bind('<Delete>', self._on_delete_key)

        # 拖拽事件 - 仅在tkinterdnd2可用时绑定
        if self.drag_drop_enabled and DRAG_DROP_AVAILABLE and TREEVIEW_SUPPORTS_DRAG:
            try:
                # 检查Treeview是否支持拖拽方法
                if hasattr(self.tree, 'drag_source_register'):
                    # 为Treeview启用内部拖拽排序
                    self.tree.drag_source_register(1, DND_FILES)
                    self.tree.drag_dest_register(DND_FILES)
                    self.tree.dnd_bind('<<DragStartCmd>>', self._on_tree_drag_start)
                    self.tree.dnd_bind('<<DragEndCmd>>', self._on_tree_drag_end)
                    self.tree.dnd_bind('<<Drop>>', self._on_tree_drop)
                    self.tree.bind('<Button-3>', self._on_right_click)  # 右键菜单支持
                    print("Treeview拖拽事件绑定成功")
                else:
                    print("当前Treeview不支持拖拽功能，可能需要tkinterdnd2增强版本")
                    self.drag_drop_enabled = False
            except Exception as e:
                print(f"绑定拖拽事件失败: {e}")
                self.drag_drop_enabled = False
        elif self.drag_drop_enabled and not TREEVIEW_SUPPORTS_DRAG:
            print("Treeview拖拽支持不可用，但按钮和键盘操作仍然可用")
            self.drag_drop_enabled = False

        # 键盘快捷键
        self.tree.bind('<Control-Up>', lambda e: self._move_selected_up())
        self.tree.bind('<Control-Down>', lambda e: self._move_selected_down())
        self.tree.bind('<Control-Home>', lambda e: self._move_selected_to_top())
        self.tree.bind('<Control-End>', lambda e: self._move_selected_to_bottom())

    def _on_item_click(self, event):
        """处理单击事件 - 单击选中项目"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # 如果点击的项目没有被选中，则选中它（单选模式）
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            else:
                # 如果点击已选中的项目，保持选中状态
                pass
        else:
            # 点击空白区域，清空选择
            self.tree.selection_set('')

        self._update_selection()

    def _on_double_click(self, event):
        """处理双击事件 - 可以用于打开文件或显示详情"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # 获取文件索引
            index = self.tree.index(item)
            if 0 <= index < len(self.file_list):
                file_info = self.file_list[index]
                file_path = file_info['file_path']

                # 可以在这里添加双击后的操作，比如：
                # - 显示文件详情
                # - 预览CBZ内容
                # - 或者其他自定义操作

                # 目前先显示一个简单的信息框
                messagebox.showinfo(
                    "文件信息",
                    f"文件名: {file_info['file_name']}\n"
                    f"大小: {FileUtils.get_file_size_str(file_path)}\n"
                    f"页数: {file_info['page_count']}\n"
                    f"路径: {file_path}"
                )

    def _on_ctrl_click(self, event):
        """处理Ctrl+点击事件"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            if item in self.tree.selection():
                self.tree.selection_remove(item)
            else:
                self.tree.selection_add(item)
        self._update_selection()

    def _on_shift_click(self, event):
        """处理Shift+点击事件"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            current_selection = self.tree.selection()
            if current_selection:
                last_selected = current_selection[-1]
                # 获取两个item之间的所有项目
                start_idx = self.tree.index(last_selected)
                end_idx = self.tree.index(item)
                if start_idx > end_idx:
                    start_idx, end_idx = end_idx, start_idx

                self.tree.selection_set(self.tree.get_children()[start_idx:end_idx+1])
            else:
                self.tree.selection_set(item)
        self._update_selection()

    def _on_delete_key(self, event):
        """处理Delete键事件"""
        self.remove_selected()

    def _on_tree_drag_start(self, event):
        """Treeview拖拽开始"""
        try:
            # 获取被拖拽的项目
            item = self.tree.identify('item', event.x_root - self.tree.winfo_rootx(),
                                     event.y_root - self.tree.winfo_rooty())
            if item:
                self.drag_start_index = self.tree.index(item)
                # 如果没有选中该项，则选中它
                if item not in self.tree.selection():
                    self.tree.selection_set(item)
                    self._update_selection()
                return self.tree.item(item, 'text')  # 返回项目标识
        except Exception as e:
            print(f"拖拽开始失败: {e}")
        return ""

    def _on_tree_drag_end(self, event):
        """Treeview拖拽结束"""
        self.drag_start_index = None

    def _on_tree_drop(self, event):
        """Treeview拖拽放下"""
        if self.drag_start_index is None:
            return

        try:
            # 获取目标位置
            x = event.x_root - self.tree.winfo_rootx()
            y = event.y_root - self.tree.winfo_rooty()

            target_item = self.tree.identify('item', x, y)
            if target_item:
                target_index = self.tree.index(target_item)
                # 根据鼠标在项目中的位置决定插入点
                bbox = self.tree.bbox(target_item)
                if bbox and y > bbox[1] + bbox[3] // 2:
                    target_index += 1  # 插入到目标项下方
            else:
                # 没有具体目标，放到列表末尾
                target_index = len(self.file_list)

            # 简单移动：只移动被拖拽的单个项目
            if 0 <= self.drag_start_index < len(self.file_list) and self.drag_start_index != target_index:
                # 调整目标索引（考虑源项目被移除的影响）
                if self.drag_start_index < target_index:
                    target_index -= 1

                # 确保目标索引在有效范围内
                target_index = max(0, min(target_index, len(self.file_list) - 1))

                self._move_item(self.drag_start_index, target_index)

        except Exception as e:
            print(f"拖拽放置失败: {e}")

    def _on_drag_enter(self, event):
        """拖拽进入事件"""
        if self.drag_drop_enabled:
            # 可以添加视觉反馈
            pass

    def _on_drag_leave(self, event):
        """拖拽离开事件"""
        # 移除视觉反馈
        pass

    def _on_right_click(self, event):
        """右键点击事件 - 预留给未来功能"""
        pass

    def _update_selection(self):
        """更新选择状态"""
        selection = self.tree.selection()
        self.selected_indices = [self.tree.index(item) for item in selection]
        if self.selection_callback:
            self.selection_callback()

    def add_files(self, file_paths: List[str]) -> None:
        """添加文件到列表"""

        for file_path in file_paths:
            try:
                # 验证文件
                if not FileUtils.is_valid_comic_file(file_path):
                    file_type = FileUtils.get_file_type(file_path)
                    if file_type == 'UNKNOWN':
                        messagebox.showwarning("警告", f"{file_path} 不是有效的漫画文件（支持CBZ和ZIP格式）")
                    else:
                        messagebox.showwarning("警告", f"{file_path} 不是有效的{file_type}文件")
                    continue

                # 检查是否已存在
                if any(f['file_path'] == file_path for f in self.file_list):
                    messagebox.showinfo("信息", f"{Path(file_path).name} 已存在")
                    continue

                # 获取文件信息
                info = FileUtils.extract_cbz_info(file_path)
                if 'error' in info:
                    messagebox.showerror("错误", f"读取文件 {file_path} 时出错: {info['error']}")
                    continue

                # 添加到列表
                self.file_list.append(info)

                # 添加到Treeview
                self.tree.insert('', 'end', text=str(len(self.file_list)),
                               values=(
                                   info['file_name'],
                                   FileUtils.get_file_size_str(file_path),
                                   info['page_count'],
                                   file_path
                               ))

            except Exception as e:
                messagebox.showerror("错误", f"添加文件 {file_path} 时出错: {str(e)}")

    def remove_selected(self) -> None:
        """删除选中的文件"""
        if not self.selected_indices:
            return

        # 按倒序删除，避免索引变化
        for index in sorted(self.selected_indices, reverse=True):
            if 0 <= index < len(self.file_list):
                del self.file_list[index]
                # 从Treeview中删除
                item = self.tree.get_children()[index]
                self.tree.delete(item)

        # 清空选择
        self.tree.selection_set('')
        self.selected_indices = []
        self._refresh_tree()

    def clear_all(self) -> None:
        """清空所有文件"""
        self.file_list.clear()
        self.tree.delete(*self.tree.get_children())
        self.selected_indices = []

    def _move_item(self, from_index: int, to_index: int) -> None:
        """移动项目位置"""
        if not (0 <= from_index < len(self.file_list) and 0 <= to_index < len(self.file_list)):
            return

        # 移动数据
        item = self.file_list.pop(from_index)
        self.file_list.insert(to_index, item)

        # 更新选中索引 - 这是关键！
        new_selected_indices = []
        for selected_idx in self.selected_indices:
            if selected_idx == from_index:
                # 被移动的项目更新到新位置
                new_selected_indices.append(to_index)
            elif from_index < selected_idx <= to_index:
                # 在移动范围内的项目向上移动一格
                new_selected_indices.append(selected_idx - 1)
            elif to_index <= selected_idx < from_index:
                # 在移动范围内的项目向下移动一格
                new_selected_indices.append(selected_idx + 1)
            else:
                # 其他项目保持不变
                new_selected_indices.append(selected_idx)

        self.selected_indices = new_selected_indices

        # 刷新Treeview
        self._refresh_tree()

    def move_selected_up(self) -> None:
        """向上移动选中的项目"""
        if not self.selected_indices:
            return

        # 找到最小的选中索引
        min_index = min(self.selected_indices)
        if min_index <= 0:
            return

        # 计算新的选择索引并一次性移动
        moves = []
        for index in sorted(self.selected_indices):
            if index > 0:
                moves.append((index, index - 1))

        # 执行所有移动
        for from_idx, to_idx in moves:
            self._move_item(from_idx, to_idx)

    def move_selected_down(self) -> None:
        """向下移动选中的项目"""
        if not self.selected_indices:
            return

        max_index = max(self.selected_indices)
        if max_index >= len(self.file_list) - 1:
            return

        # 计算新的选择索引并一次性移动（倒序）
        moves = []
        for index in sorted(self.selected_indices, reverse=True):
            if index < len(self.file_list) - 1:
                moves.append((index, index + 1))

        # 执行所有移动
        for from_idx, to_idx in moves:
            self._move_item(from_idx, to_idx)

    def move_selected_to_top(self) -> None:
        """移动选中的项目到顶部"""
        if not self.selected_indices:
            return

        # 获取要移动的项目（按原始顺序）
        selected_items = [self.file_list[i] for i in sorted(self.selected_indices) if i > 0]

        # 移除原位置的项目（倒序，避免索引变化）
        for index in sorted(self.selected_indices, reverse=True):
            if index > 0:
                del self.file_list[index]

        # 插入到顶部（保持原始顺序）
        insert_pos = 0
        for item in selected_items:
            self.file_list.insert(insert_pos, item)
            insert_pos += 1

        # 更新选择索引
        self.selected_indices = list(range(len(selected_items)))

        self._refresh_tree()

    def move_selected_to_bottom(self) -> None:
        """移动选中的项目到底部"""
        if not self.selected_indices:
            return

        # 获取要移动的项目（按原始顺序）
        selected_items = [self.file_list[i] for i in sorted(self.selected_indices)]

        # 移除原位置的项目（倒序，避免索引变化）
        for index in sorted(self.selected_indices, reverse=True):
            del self.file_list[index]

        # 获取新的列表长度
        new_length = len(self.file_list)

        # 插入到底部（保持原始顺序）
        for item in selected_items:
            self.file_list.append(item)

        # 更新选择索引
        start_idx = new_length
        end_idx = len(self.file_list)
        self.selected_indices = list(range(start_idx, end_idx))

        self._refresh_tree()

    def _refresh_tree(self) -> None:
        """刷新Treeview显示"""
        # 清空并重新填充
        self.tree.delete(*self.tree.get_children())

        # 创建所有项目
        tree_items = []
        for i, info in enumerate(self.file_list):
            item = self.tree.insert('', 'end', text=str(i + 1),
                                  values=(
                                      info['file_name'],
                                      FileUtils.get_file_size_str(info['file_path']),
                                      info['page_count'],
                                      info['file_path']
                                  ))
            tree_items.append(item)

        # 直接使用索引恢复选择 - 更可靠！
        for selected_idx in self.selected_indices:
            if 0 <= selected_idx < len(tree_items):
                self.tree.selection_add(tree_items[selected_idx])

        self._update_selection()

    def get_file_paths(self) -> List[str]:
        """获取所有文件路径"""
        return [info['file_path'] for info in self.file_list]

    def get_selected_file_paths(self) -> List[str]:
        """获取选中文件的路径"""
        return [self.file_list[i]['file_path'] for i in self.selected_indices if i < len(self.file_list)]

    def set_selection_callback(self, callback: Callable) -> None:
        """设置选择回调函数"""
        self.selection_callback = callback