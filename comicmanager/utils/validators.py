"""
输入验证模块
提供各种输入验证功能
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional


class InputValidator:
    """输入验证器类"""

    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
        """
        验证文件名是否有效

        Returns:
            (是否有效, 错误信息)
        """
        if not filename or not filename.strip():
            return False, "文件名不能为空"

        filename = filename.strip()

        # 检查非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            if char in filename:
                return False, f"文件名包含非法字符: {char}"

        # 检查保留名称 (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]

        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            return False, f"文件名使用了保留名称: {name_without_ext}"

        # 检查文件名长度
        if len(filename) > 255:
            return False, "文件名过长（最大255字符）"

        # 检查是否以点或空格开头/结尾
        if filename.startswith('.') or filename.startswith(' ') or filename.endswith('.') or filename.endswith(' '):
            return False, "文件名不能以点或空格开头或结尾"

        return True, None

    @staticmethod
    def validate_directory_path(directory: str) -> Tuple[bool, Optional[str]]:
        """
        验证目录路径是否有效

        Returns:
            (是否有效, 错误信息)
        """
        if not directory or not directory.strip():
            return False, "目录路径不能为空"

        try:
            path = Path(directory.strip())

            # 检查路径格式
            if any(char in str(path) for char in '<>:"|?*'):
                return False, "目录路径包含非法字符"

            # 如果路径存在，检查是否为目录
            if path.exists():
                if not path.is_dir():
                    return False, "指定路径不是目录"

                # 检查是否可写
                if not path.is_dir() or not path.exists():
                    return False, "目录不存在"

            # 检查路径长度
            if len(str(path)) > 260:  # Windows限制
                return False, "路径过长（最大260字符）"

            return True, None

        except Exception as e:
            return False, f"目录路径格式错误: {str(e)}"

    @staticmethod
    def validate_cbz_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证CBZ文件是否有效

        Returns:
            (是否有效, 错误信息)
        """
        if not file_path or not file_path.strip():
            return False, "文件路径不能为空"

        try:
            path = Path(file_path.strip())

            # 检查文件是否存在
            if not path.exists():
                return False, "文件不存在"

            # 检查是否为文件
            if not path.is_file():
                return False, "指定路径不是文件"

            # 检查文件扩展名
            if path.suffix.lower() != '.cbz':
                return False, "不是CBZ文件（扩展名应为.cbz）"

            # 检查文件大小
            if path.stat().st_size == 0:
                return False, "文件为空"

            # 尝试作为ZIP文件打开
            import zipfile
            try:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    # 检查是否有有效内容
                    files = zf.namelist()
                    if not files:
                        return False, "CBZ文件为空"

                    # 检查是否有图片文件
                    has_images = any(
                        f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'))
                        for f in files
                    )
                    if not has_images:
                        return False, "CBZ文件中没有找到图片文件"

            except zipfile.BadZipFile:
                return False, "CBZ文件格式错误或已损坏"

            return True, None

        except Exception as e:
            return False, f"验证CBZ文件时出错: {str(e)}"

    @staticmethod
    def validate_output_path(output_path: str, overwrite: bool = False) -> Tuple[bool, Optional[str]]:
        """
        验证输出路径是否有效

        Args:
            output_path: 输出文件路径
            overwrite: 是否允许覆盖现有文件

        Returns:
            (是否有效, 错误信息)
        """
        if not output_path or not output_path.strip():
            return False, "输出路径不能为空"

        try:
            path = Path(output_path.strip())

            # 验证文件名
            is_valid, error = InputValidator.validate_filename(path.name)
            if not is_valid:
                return False, error

            # 验证目录路径
            is_valid, error = InputValidator.validate_directory_path(str(path.parent))
            if not is_valid:
                return False, error

            # 检查目录是否可写
            if path.parent.exists():
                import os
                if not os.access(path.parent, os.W_OK):
                    return False, "目录不可写"

            # 检查文件是否已存在
            if path.exists():
                if not overwrite:
                    return False, f"文件已存在: {path.name}"

                if not path.is_file():
                    return False, "目标路径已存在但不是文件"

            # 检查文件扩展名
            if path.suffix.lower() != '.cbz':
                return False, "输出文件必须使用.cbz扩展名"

            return True, None

        except Exception as e:
            return False, f"验证输出路径时出错: {str(e)}"

    @staticmethod
    def validate_file_list(file_paths: List[str]) -> Tuple[bool, Optional[str], List[str]]:
        """
        验证文件列表

        Returns:
            (是否全部有效, 错误信息, 有效文件列表)
        """
        if not file_paths:
            return False, "没有选择文件", []

        valid_files = []
        errors = []

        for file_path in file_paths:
            is_valid, error = InputValidator.validate_cbz_file(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                errors.append(f"{Path(file_path).name}: {error}")

        if not valid_files:
            return False, "没有有效的CBZ文件", []

        if errors:
            error_msg = "部分文件无效:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... 以及 {len(errors) - 5} 个其他文件"
            return False, error_msg, valid_files

        return True, None, valid_files

    @staticmethod
    def validate_numeric_input(value: str, min_val: Optional[int] = None,
                              max_val: Optional[int] = None) -> Tuple[bool, Optional[int]]:
        """
        验证数值输入

        Returns:
            (是否有效, 验证后的数值)
        """
        if not value or not value.strip():
            return False, None

        try:
            num = int(value.strip())

            if min_val is not None and num < min_val:
                return False, None

            if max_val is not None and num > max_val:
                return False, None

            return True, num

        except ValueError:
            return False, None