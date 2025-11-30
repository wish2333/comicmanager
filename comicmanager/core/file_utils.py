"""
文件操作工具模块
提供文件相关的实用功能
"""

import os
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import tempfile
import shutil


class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def is_valid_cbz_file(file_path: str) -> bool:
        """检查是否为有效的CBZ文件"""
        try:
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                return False

            # 检查文件扩展名
            if path.suffix.lower() != '.cbz':
                return False

            # 检查是否为有效的ZIP文件
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 尝试读取文件列表
                zf.namelist()
                return True
        except Exception:
            return False

    @staticmethod
    def extract_cbz_info(file_path: str) -> Dict[str, Any]:
        """提取CBZ文件信息"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                file_list = zf.namelist()

                # 查找ComicInfo.xml
                comic_info = None
                for file_name in file_list:
                    if file_name.lower().endswith('comicinfo.xml'):
                        try:
                            comic_info = zf.read(file_name).decode('utf-8')
                        except:
                            pass
                        break

                # 获取图片文件列表
                image_files = [f for f in file_list if
                              f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'))]
                image_files.sort()

                return {
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'file_size': Path(file_path).stat().st_size,
                    'page_count': len(image_files),
                    'image_files': image_files,
                    'comic_info': comic_info,
                    'total_files': len(file_list)
                }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_file_size_str(file_path: str) -> str:
        """获取文件大小的字符串表示"""
        try:
            size = Path(file_path).stat().st_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除非法字符"""
        # Windows非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')

        # 移除前后空格和点
        filename = filename.strip(' .')

        # 确保文件名不为空
        if not filename:
            filename = "unnamed"

        return filename

    @staticmethod
    def get_unique_filename(directory: str, base_name: str, extension: str = '.cbz') -> str:
        """获取唯一的文件名，避免重复"""
        base_path = Path(directory)
        base_name = FileUtils.sanitize_filename(base_name)

        counter = 1
        filename = f"{base_name}{extension}"

        while (base_path / filename).exists():
            filename = f"{base_name}_{counter}{extension}"
            counter += 1

        return filename

    @staticmethod
    def create_temp_directory() -> str:
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp(prefix='comicmanager_')
        return temp_dir

    @staticmethod
    def cleanup_temp_directory(temp_dir: str) -> None:
        """清理临时目录"""
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

    @staticmethod
    def validate_output_path(output_path: str, overwrite: bool = False) -> Tuple[bool, str]:
        """验证输出路径是否有效"""
        try:
            path = Path(output_path)

            # 检查目录是否存在
            if not path.parent.exists():
                return False, f"目录不存在: {path.parent}"

            # 检查是否可写
            if not os.access(path.parent, os.W_OK):
                return False, f"目录不可写: {path.parent}"

            # 检查文件是否已存在
            if path.exists() and not overwrite:
                return False, f"文件已存在: {output_path}"

            return True, "路径有效"
        except Exception as e:
            return False, f"路径验证失败: {str(e)}"