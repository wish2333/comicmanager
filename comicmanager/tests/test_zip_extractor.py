"""
ZIP提取器测试模块
"""

import unittest
import tempfile
import shutil
import zipfile
from pathlib import Path
from typing import List

from ..core.zip_extractor import ZIPExtractor, ExtractionProgress
from ..core.file_utils import FileUtils


class TestZIPExtractor(unittest.TestCase):
    """ZIP提取器测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.zip_extractor = ZIPExtractor(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        self.zip_extractor.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_zip(self, zip_path: Path, files_data: List[tuple]) -> None:
        """创建测试ZIP文件

        Args:
            zip_path: ZIP文件路径
            files_data: 文件数据列表，每个元素为(filename, content)元组
        """
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for filename, content in files_data:
                if isinstance(content, bytes):
                    zf.writestr(filename, content)
                else:
                    zf.writestr(filename, content.encode('utf-8'))

    def test_validate_valid_zip_with_images(self):
        """测试包含图片的有效ZIP文件验证"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_images.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.png', b'fake_png_content'),
            ('image3.webp', b'fake_webp_content'),
            ('other.txt', 'text content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 验证ZIP文件
        result = self.zip_extractor.validate_zip_file(str(zip_path))

        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
        self.assertEqual(len(result['image_files']), 3)
        self.assertIn('jpg', result['supported_formats'])
        self.assertIn('png', result['supported_formats'])
        self.assertIn('webp', result['supported_formats'])

    def test_validate_zip_without_images(self):
        """测试不包含图片的ZIP文件验证"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_no_images.zip"
        files_data = [
            ('document.txt', 'text content'),
            ('data.json', '{"key": "value"}')
        ]
        self._create_test_zip(zip_path, files_data)

        # 验证ZIP文件
        result = self.zip_extractor.validate_zip_file(str(zip_path))

        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        self.assertEqual(len(result['image_files']), 0)

    def test_validate_invalid_zip_file(self):
        """测试无效ZIP文件验证"""
        # 创建无效文件
        zip_path = Path(self.temp_dir) / "invalid.zip"
        zip_path.write_text("not a zip file")

        # 验证ZIP文件
        result = self.zip_extractor.validate_zip_file(str(zip_path))

        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])

    def test_validate_nonexistent_file(self):
        """测试不存在的文件验证"""
        result = self.zip_extractor.validate_zip_file("nonexistent.zip")

        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])

    def test_extract_images_default_formats(self):
        """测试使用默认格式提取图片"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_extract.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.jpeg', b'fake_jpeg_content'),
            ('image3.png', b'fake_png_content'),
            ('image4.webp', b'fake_webp_content'),
            ('document.txt', 'text content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 创建输出目录
        output_dir = Path(self.temp_dir) / "output"
        output_dir.mkdir(exist_ok=True)

        # 提取图片（默认只提取JPG格式）
        result = self.zip_extractor.extract_images(
            str(zip_path),
            str(output_dir),
            {'jpg', 'jpeg'}
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['total_extracted'], 2)  # jpg和jpeg
        self.assertEqual(len(result['extracted_files']), 2)

        # 检查提取的文件
        extracted_files = list(output_dir.glob("*"))
        self.assertEqual(len(extracted_files), 2)

        # 验证文件名格式（应该按顺序编号）
        filenames = [f.name for f in sorted(extracted_files)]
        expected_filenames = ['0001.jpg', '0002.jpeg']
        self.assertEqual(filenames, expected_filenames)

    def test_extract_images_multiple_formats(self):
        """测试提取多种格式的图片"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_multi_formats.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.png', b'fake_png_content'),
            ('image3.webp', b'fake_webp_content'),
            ('image4.gif', b'fake_gif_content'),
            ('document.txt', 'text content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 创建输出目录
        output_dir = Path(self.temp_dir) / "output_multi"
        output_dir.mkdir(exist_ok=True)

        # 提取多种格式的图片
        result = self.zip_extractor.extract_images(
            str(zip_path),
            str(output_dir),
            {'jpg', 'png', 'webp'}
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['total_extracted'], 3)
        self.assertEqual(len(result['extracted_files']), 3)

    def test_extract_images_no_matching_formats(self):
        """测试没有匹配格式的图片提取"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_no_match.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.png', b'fake_png_content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 创建输出目录
        output_dir = Path(self.temp_dir) / "output_no_match"
        output_dir.mkdir(exist_ok=True)

        # 提取不存在的格式
        result = self.zip_extractor.extract_images(
            str(zip_path),
            str(output_dir),
            {'webp', 'gif'}
        )

        self.assertFalse(result['success'])
        self.assertIsNotNone(result['error'])

    def test_extract_to_temp(self):
        """测试提取到临时目录"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_temp.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.png', b'fake_png_content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 提取到临时目录
        result = self.zip_extractor.extract_to_temp(
            str(zip_path),
            {'jpg'}
        )

        self.assertTrue(result['success'])
        self.assertIn('temp_dir', result)
        self.assertTrue(Path(result['temp_dir']).exists())

        # 清理临时目录
        self.zip_extractor.cleanup_temp_dir(result['temp_dir'])

    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        formats = self.zip_extractor.get_supported_formats()

        self.assertIsInstance(formats, list)
        self.assertIn('jpg', formats)
        self.assertIn('png', formats)
        self.assertIn('webp', formats)

    def test_parse_format_string(self):
        """测试解析格式字符串"""
        # 测试单个格式
        formats = self.zip_extractor.parse_format_string("jpg")
        self.assertEqual(formats, {'jpg'})

        # 测试多个格式
        formats = self.zip_extractor.parse_format_string("jpg,png,webp")
        self.assertEqual(formats, {'jpg', 'png', 'webp'})

        # 测试混合大小写
        formats = self.zip_extractor.parse_format_string("JPG,PNG")
        self.assertEqual(formats, {'jpg', 'png'})

        # 测试空字符串
        formats = self.zip_extractor.parse_format_string("")
        self.assertEqual(formats, {'jpg'})  # 默认格式

        # 测试无效格式
        formats = self.zip_extractor.parse_format_string("invalid,doc,txt")
        self.assertEqual(formats, {'jpg'})  # 默认格式

    def test_progress_callback(self):
        """测试进度回调功能"""
        progress_calls = []

        def progress_callback(progress: ExtractionProgress):
            progress_calls.append(progress)

        self.zip_extractor.set_progress_callback(progress_callback)

        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "test_progress.zip"
        files_data = [
            ('image1.jpg', b'fake_jpg_content'),
            ('image2.png', b'fake_png_content')
        ]
        self._create_test_zip(zip_path, files_data)

        # 创建输出目录
        output_dir = Path(self.temp_dir) / "output_progress"
        output_dir.mkdir(exist_ok=True)

        # 提取图片
        self.zip_extractor.extract_images(
            str(zip_path),
            str(output_dir),
            {'jpg', 'png'}
        )

        # 验证进度回调被调用
        self.assertGreater(len(progress_calls), 0)

        # 验证进度信息格式
        for progress in progress_calls:
            self.assertIsInstance(progress, ExtractionProgress)
            self.assertIsInstance(progress.zip_file, str)
            self.assertIsInstance(progress.current_file, str)
            self.assertIsInstance(progress.extracted_count, int)
            self.assertIsInstance(progress.total_files, int)
            self.assertIsInstance(progress.message, str)


class TestFileUtilsZIPExtension(unittest.TestCase):
    """FileUtils ZIP扩展功能测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_zip(self, zip_path: Path, files_data: List[tuple]) -> None:
        """创建测试ZIP文件"""
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for filename, content in files_data:
                if isinstance(content, bytes):
                    zf.writestr(filename, content)
                else:
                    zf.writestr(filename, content.encode('utf-8'))

    def test_is_valid_zip_file(self):
        """测试ZIP文件有效性检查"""
        # 创建包含图片的ZIP文件
        zip_path = Path(self.temp_dir) / "test.zip"
        files_data = [('image1.jpg', b'content')]
        self._create_test_zip(zip_path, files_data)

        self.assertTrue(FileUtils.is_valid_zip_file(str(zip_path)))

    def test_is_valid_zip_file_no_images(self):
        """测试不包含图片的ZIP文件"""
        # 创建不包含图片的ZIP文件
        zip_path = Path(self.temp_dir) / "test_no_images.zip"
        files_data = [('document.txt', 'content')]
        self._create_test_zip(zip_path, files_data)

        self.assertFalse(FileUtils.is_valid_zip_file(str(zip_path)))

    def test_is_valid_comic_file_zip(self):
        """测试漫画文件有效性检查（ZIP格式）"""
        # 创建包含图片的ZIP文件
        zip_path = Path(self.temp_dir) / "comic.zip"
        files_data = [('page1.jpg', b'content')]
        self._create_test_zip(zip_path, files_data)

        self.assertTrue(FileUtils.is_valid_comic_file(str(zip_path)))

    def test_get_file_type_zip(self):
        """测试获取文件类型（ZIP格式）"""
        # 创建包含图片的ZIP文件
        zip_path = Path(self.temp_dir) / "comic.zip"
        files_data = [('page1.jpg', b'content')]
        self._create_test_zip(zip_path, files_data)

        file_type = FileUtils.get_file_type(str(zip_path))
        self.assertEqual(file_type, 'ZIP')

    def test_extract_comic_info_zip(self):
        """测试提取ZIP漫画文件信息"""
        # 创建测试ZIP文件
        zip_path = Path(self.temp_dir) / "comic_info.zip"
        files_data = [
            ('page1.jpg', b'fake_jpg_content'),
            ('page2.png', b'fake_png_content'),
            ('ComicInfo.xml', '<?xml version="1.0"?><ComicInfo><Title>Test Comic</Title></ComicInfo>')
        ]
        self._create_test_zip(zip_path, files_data)

        info = FileUtils.extract_comic_info(str(zip_path))

        self.assertNotIn('error', info)
        self.assertEqual(info['file_type'], 'ZIP')
        self.assertEqual(info['page_count'], 2)
        self.assertEqual(len(info['image_files']), 2)
        self.assertIsNotNone(info['comic_info'])


if __name__ == '__main__':
    unittest.main()