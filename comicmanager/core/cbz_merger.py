"""
CBZ文件合并器核心模块
实现CBZ文件的主要合并逻辑
"""

import os
import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class MergeProgress:
    """合并进度信息"""
    current_file: str
    current_progress: int
    total_progress: int
    message: str


class CBZMerger:
    """CBZ文件合并器"""

    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix='comicmanager_')
        self.progress_callback: Optional[Callable[[MergeProgress], None]] = None

    def set_progress_callback(self, callback: Callable[[MergeProgress], None]) -> None:
        """设置进度回调函数"""
        self.progress_callback = callback

    def _report_progress(self, current_file: str, current: int, total: int, message: str) -> None:
        """报告合并进度"""
        if self.progress_callback:
            progress = MergeProgress(current_file, current, total, message)
            self.progress_callback(progress)

    def validate_cbz_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """验证CBZ文件的有效性"""
        from .file_utils import FileUtils

        results = {
            'valid_files': [],
            'invalid_files': [],
            'total_size': 0,
            'total_pages': 0,
            'errors': []
        }

        for file_path in file_paths:
            try:
                if not FileUtils.is_valid_cbz_file(file_path):
                    results['invalid_files'].append({
                        'path': file_path,
                        'error': '不是有效的CBZ文件'
                    })
                    continue

                info = FileUtils.extract_cbz_info(file_path)
                if 'error' in info:
                    results['invalid_files'].append({
                        'path': file_path,
                        'error': info['error']
                    })
                    continue

                results['valid_files'].append(info)
                results['total_size'] += info['file_size']
                results['total_pages'] += info['page_count']

            except Exception as e:
                results['errors'].append(f"验证文件 {file_path} 时出错: {str(e)}")
                results['invalid_files'].append({
                    'path': file_path,
                    'error': str(e)
                })

        return results

    def merge_cbz_files(self, file_paths: List[str], output_path: str,
                        preserve_metadata: bool = True) -> Dict[str, Any]:
        """
        合并多个CBZ文件

        Args:
            file_paths: 要合并的CBZ文件路径列表
            output_path: 输出文件路径
            preserve_metadata: 是否保留原始元数据

        Returns:
            包含合并结果和统计信息的字典
        """
        from .file_utils import FileUtils

        # 验证输入文件
        validation_result = self.validate_cbz_files(file_paths)
        if validation_result['invalid_files']:
            return {
                'success': False,
                'error': '部分文件无效',
                'invalid_files': validation_result['invalid_files']
            }

        # 验证输出路径
        valid, error_msg = FileUtils.validate_output_path(output_path)
        if not valid:
            return {'success': False, 'error': error_msg}

        result = {
            'success': False,
            'output_path': output_path,
            'merged_files': [],
            'total_pages': 0,
            'errors': []
        }

        try:
            # 创建临时工作目录
            work_dir = tempfile.mkdtemp(prefix='comicmanager_merge_')
            page_number = 1
            merged_info = []

            # 解压所有CBZ文件到临时目录
            for i, file_path in enumerate(file_paths):
                self._report_progress(
                    file_path,
                    i,
                    len(file_paths),
                    f"正在处理文件 {i+1}/{len(file_paths)}"
                )

                try:
                    # 解压当前CBZ文件
                    temp_extract_dir = tempfile.mkdtemp(prefix='comicmanager_extract_')

                    with zipfile.ZipFile(file_path, 'r') as zf:
                        zf.extractall(temp_extract_dir)

                    # 获取图片文件并重命名
                    info = FileUtils.extract_cbz_info(file_path)
                    image_files = info['image_files']

                    # 复制并重命名图片文件
                    for img_file in image_files:
                        src_path = Path(temp_extract_dir) / img_file
                        if src_path.exists():
                            # 生成新的文件名
                            ext = Path(img_file).suffix
                            new_name = f"{page_number:04d}{ext}"
                            dst_path = Path(work_dir) / new_name

                            # 复制文件
                            shutil.copy2(src_path, dst_path)
                            page_number += 1

                    # 清理解压目录
                    shutil.rmtree(temp_extract_dir, ignore_errors=True)

                    # 保存文件信息
                    merged_info.append({
                        'path': file_path,
                        'name': Path(file_path).name,
                        'pages': len(image_files)
                    })

                except Exception as e:
                    error_msg = f"处理文件 {file_path} 时出错: {str(e)}"
                    result['errors'].append(error_msg)
                    continue

            # 创建新的CBZ文件
            result['total_pages'] = page_number - 1
            self._report_progress("创建输出文件", len(file_paths), len(file_paths), "正在创建合并后的CBZ文件")

            # 收集所有图片文件
            output_images = []
            for file_path in sorted(Path(work_dir).glob('*')):
                if file_path.is_file() and file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']:
                    output_images.append(file_path)

            # 创建新的CBZ文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # 添加图片文件
                for img_path in output_images:
                    zf.write(img_path, img_path.name)

                # 如果需要保留元数据，创建合并后的ComicInfo.xml
                if preserve_metadata and len(merged_info) > 0:
                    comic_info_xml = self._create_merged_comic_info(merged_info)
                    zf.writestr('ComicInfo.xml', comic_info_xml)

            result['success'] = True
            result['merged_files'] = merged_info

            # 清理临时目录
            shutil.rmtree(work_dir, ignore_errors=True)

        except Exception as e:
            result['success'] = False
            result['errors'].append(f"合并过程中出错: {str(e)}")

        finally:
            # 确保清理临时目录
            if 'work_dir' in locals():
                shutil.rmtree(work_dir, ignore_errors=True)

        return result

    def _create_merged_comic_info(self, merged_info: List[Dict[str, Any]]) -> str:
        """创建合并后的ComicInfo.xml内容"""
        # 创建根元素
        comic_info = ET.Element('ComicInfo')
        comic_info.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        comic_info.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        # 添加基本信息
        title_elem = ET.SubElement(comic_info, 'Title')
        title_elem.text = '合并漫画'

        summary_elem = ET.SubElement(comic_info, 'Summary')
        summary_elem.text = f'由 {len(merged_info)} 个文件合并而成'

        # 添加源文件信息
        for i, info in enumerate(merged_info):
            file_elem = ET.SubElement(comic_info, f'SourceFile{i+1}')
            file_elem.text = info['name']

        # 返回XML字符串
        return ET.tostring(comic_info, encoding='unicode', xml_declaration=True)

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