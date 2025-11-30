"""
ZIP文件图片提取器模块
用于从ZIP文件中提取图片并支持格式过滤
"""

import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Set, Dict, Any, Callable
from dataclasses import dataclass


# 可用的图片格式
SUPPORTED_IMAGE_FORMATS = {'jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'}


@dataclass
class ExtractionProgress:
    """ZIP提取进度信息"""
    zip_file: str
    current_file: str
    extracted_count: int
    total_files: int
    message: str


class ZIPExtractor:
    """ZIP文件图片提取器"""

    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix='comicmanager_zip_')
        self.progress_callback: Optional[Callable[[ExtractionProgress], None]] = None

    def set_progress_callback(self, callback: Callable[[ExtractionProgress], None]) -> None:
        """设置进度回调函数"""
        self.progress_callback = callback

    def _report_progress(self, zip_file: str, current_file: str, current: int, total: int, message: str) -> None:
        """报告提取进度"""
        if self.progress_callback:
            progress = ExtractionProgress(zip_file, current_file, current, total, message)
            self.progress_callback(progress)

    def validate_zip_file(self, zip_path: str) -> Dict[str, Any]:
        """
        验证ZIP文件的有效性并扫描图片文件

        Args:
            zip_path: ZIP文件路径

        Returns:
            包含验证结果和文件信息的字典
        """
        result = {
            'valid': False,
            'error': None,
            'image_files': [],
            'total_files': 0,
            'supported_formats': set(),
            'file_size': 0
        }

        try:
            path = Path(zip_path)
            if not path.exists() or not path.is_file():
                result['error'] = '文件不存在或不是文件'
                return result

            # 检查文件扩展名
            if path.suffix.lower() != '.zip':
                result['error'] = '不是ZIP文件'
                return result

            # 获取文件大小
            result['file_size'] = path.stat().st_size

            # 检查ZIP文件结构
            with zipfile.ZipFile(zip_path, 'r') as zf:
                file_list = zf.namelist()
                result['total_files'] = len(file_list)

                # 扫描图片文件
                image_files = []
                for file_name in file_list:
                    # 跳过目录和空路径
                    if not file_name or file_name.endswith('/'):
                        continue

                    # 安全检查：防止路径遍历攻击
                    if '..' in file_name or file_name.startswith('/'):
                        continue

                    # 获取文件扩展名（去掉点号）
                    ext = Path(file_name).suffix.lower().lstrip('.')
                    if ext in SUPPORTED_IMAGE_FORMATS:
                        # 获取文件信息
                        file_info = zf.getinfo(file_name)
                        # 检查文件大小是否合理（避免过大文件）
                        if file_info.file_size > 100 * 1024 * 1024:  # 100MB限制
                            print(f"警告: 跳过过大的图片文件 {file_name} ({file_info.file_size} bytes)")
                            continue

                        image_files.append({
                            'name': file_name,
                            'path': file_name,
                            'extension': ext,
                            'size': file_info.file_size,
                            'compressed_size': file_info.compress_size,
                            'date_time': file_info.date_time
                        })
                        result['supported_formats'].add(ext)

                # 按文件名排序（支持数字和字母排序）
                def natural_sort_key(file_info: Dict[str, Any]) -> List:
                    """自然排序键函数"""
                    import re
                    name = file_info['name']
                    # 提取目录部分和文件名部分
                    parts = name.split('/')
                    filename = parts[-1] if parts else name

                    # 分离数字和非数字部分进行自然排序
                    result = []
                    for text in re.split(r'(\d+)', filename):
                        if text.isdigit():
                            result.append(int(text))
                        else:
                            result.append(text.lower())
                    return result

                image_files.sort(key=natural_sort_key)
                result['image_files'] = image_files

                if image_files:
                    result['valid'] = True
                    result['supported_formats'] = SUPPORTED_IMAGE_FORMATS.copy()
                else:
                    result['error'] = 'ZIP文件中未找到支持的图片文件 (JPG, JPEG, PNG, WEBP, GIF, BMP)'

        except zipfile.BadZipFile:
            result['error'] = 'ZIP文件损坏或格式无效'
        except PermissionError:
            result['error'] = '无法访问文件，权限不足'
        except UnicodeDecodeError:
            result['error'] = 'ZIP文件包含无效的文件名编码'
        except Exception as e:
            result['error'] = f'验证ZIP文件时出错: {str(e)}'

        return result

    def extract_images(self, zip_path: str, output_dir: str,
                       image_formats: Optional[Set[str]] = None,
                       chapter_prefix: str = "ch1") -> Dict[str, Any]:
        """
        从ZIP文件中提取指定格式的图片

        Args:
            zip_path: ZIP文件路径
            output_dir: 输出目录
            image_formats: 要提取的图片格式集合
            chapter_prefix: 章节前缀，如 "ch1", "ch2" 等

        Returns:
            包含提取结果和统计信息的字典
        """
        result = {
            'success': False,
            'error': None,
            'extracted_files': [],
            'total_extracted': 0
        }

        try:
            # 标准化路径
            zip_path = os.path.normpath(zip_path)

            path = Path(zip_path)
            if not path.exists() or not path.is_file():
                result['error'] = 'ZIP文件不存在'
                return result

            # 检查文件扩展名
            if path.suffix.lower() != '.zip':
                result['error'] = '不是ZIP文件'
                return result

            # 验证ZIP文件
            validation_result = self.validate_zip_file(zip_path)
            if not validation_result['valid']:
                result['error'] = validation_result['error']
                return result

            # 确保输出目录存在
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 打开ZIP文件进行提取
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # 筛选要提取的图片文件
                target_files = []
                for img_file in validation_result['image_files']:
                    if img_file['extension'] in image_formats:
                        target_files.append(img_file)

                if not target_files:
                    result['error'] = f'ZIP文件中没有找到指定格式的图片: {", ".join(image_formats)}'
                    return result

                total_files = len(target_files)
                extracted_count = 0

                # 提取文件
                for i, img_file in enumerate(target_files):
                    zip_filename = img_file['name']
                    self._report_progress(
                        zip_path, zip_filename, i + 1, total_files,
                        f"正在提取: {zip_filename}"
                    )

                    try:
                        with zf.open(zip_filename) as f:
                            image_data = f.read()

                        # 无压缩模式：直接使用原始图片数据
                        # 文件名格式: chX_000Y.ext
                        ext = img_file['extension']
                        new_name = f"{chapter_prefix}_{i+1:03d}.{ext}"
                        new_path = Path(output_dir) / new_name

                        print(f"  {i+1:2d}. 重命名: {zip_filename} -> {new_name}")

                        with open(new_path, 'wb') as out_f:
                            out_f.write(image_data)

                        extracted_count += 1
                        print(f"    ✅ 成功提取并重命名: {zip_filename}")

                    except Exception as e:
                        print(f"    ❌ 提取文件 {zip_filename} 失败: {e}")
                        continue

                result['success'] = True
                result['total_extracted'] = extracted_count

        except zipfile.BadZipFile:
            result['error'] = 'ZIP文件损坏或格式无效'
        except PermissionError:
            result['error'] = '无法访问文件，权限不足'
        except Exception as e:
            result['error'] = f'提取图片时出错: {str(e)}'

        return result

    def extract_to_temp(self, zip_path: str,
                        image_formats: Optional[Set[str]] = None,
                        chapter_prefix: str = "ch1") -> Dict[str, Any]:
        """提取到临时目录"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix='comicmanager_extract_')
        result = self.extract_images(zip_path, temp_dir, image_formats, chapter_prefix)
        result['temp_dir'] = temp_dir
        return result

    def cleanup_temp_dir(self, temp_dir: str) -> None:
        """清理临时目录"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    def get_supported_formats(self) -> List[str]:
        """获取支持的格式列表"""
        return sorted(list(SUPPORTED_IMAGE_FORMATS))

    def parse_format_string(self, format_string: str) -> Set[str]:
        """
        解析格式字符串为格式集合

        Args:
            format_string: 逗号分隔的格式字符串，例如 "jpg,png,webp"

        Returns:
            格式集合
        """
        if not format_string:
            return {'jpg'}  # 默认格式

        formats = set()
        for fmt in format_string.split(','):
            fmt = fmt.strip().lstrip('.')
            if fmt in SUPPORTED_IMAGE_FORMATS:
                formats.add(fmt)

        # 如果没有有效格式，使用默认格式
        if not formats:
            formats.add('jpg')

        return formats

    def cleanup(self) -> None:
        """清理临时文件"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    def __del__(self):
        """析构函数，确保清理资源"""
        self.cleanup()