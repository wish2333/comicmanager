"""
CBZ合并器测试用例
手动测试指导和自动化测试
"""

import unittest
import tempfile
import shutil
import zipfile
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from comicmanager.core.cbz_merger import CBZMerger, MergeProgress
from comicmanager.core.file_utils import FileUtils
from comicmanager.utils.validators import InputValidator


class TestCBZMerger(unittest.TestCase):
    """CBZ合并器测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp(prefix='comicmanager_test_')
        self.merger = CBZMerger()
        self.test_files = []

    def tearDown(self):
        """测试后清理"""
        self.merger.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_cbz(self, name: str, num_pages: int = 3) -> str:
        """创建测试用的CBZ文件"""
        cbz_path = Path(self.temp_dir) / f"{name}.cbz"

        # 创建测试图片文件
        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加ComicInfo.xml
            comic_info = f'''<?xml version="1.0"?>
<ComicInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <Title>{name}</Title>
    <Series>Test Series</Series>
    <Number>{name.split()[-1]}</Number>
    <Summary>测试用CBZ文件</Summary>
    <LanguageISO>zh</LanguageISO>
</ComicInfo>'''
            zf.writestr('ComicInfo.xml', comic_info)

            # 添加测试图片文件（创建小的测试图片）
            for i in range(1, num_pages + 1):
                page_content = f"Test page {i} content - {name}".encode('utf-8')
                zf.writestr(f"{i:03d}.jpg", page_content)

        self.test_files.append(str(cbz_path))
        return str(cbz_path)

    def test_create_test_cbz(self):
        """测试创建CBZ文件"""
        cbz_path = self.create_test_cbz("test_volume_1", 5)
        self.assertTrue(Path(cbz_path).exists())

        # 验证CBZ文件
        self.assertTrue(FileUtils.is_valid_cbz_file(cbz_path))

        # 验证内容
        info = FileUtils.extract_cbz_info(cbz_path)
        self.assertEqual(info['page_count'], 5)
        self.assertTrue('comic_info' in info)

    def test_validate_cbz_files(self):
        """测试CBZ文件验证"""
        # 创建测试文件
        file1 = self.create_test_cbz("volume_1", 3)
        file2 = self.create_test_cbz("volume_2", 4)

        # 测试有效文件
        result = self.merger.validate_cbz_files([file1, file2])
        self.assertEqual(len(result['valid_files']), 2)
        self.assertEqual(result['total_pages'], 7)
        self.assertEqual(len(result['invalid_files']), 0)

    def test_merge_cbz_files(self):
        """测试CBZ文件合并"""
        # 创建测试文件
        file1 = self.create_test_cbz("volume_1", 3)
        file2 = self.create_test_cbz("volume_2", 4)
        output_path = Path(self.temp_dir) / "merged_output.cbz"

        # 合并文件
        result = self.merger.merge_cbz_files([file1, file2], str(output_path))

        # 验证结果
        self.assertTrue(result['success'])
        self.assertTrue(output_path.exists())
        self.assertEqual(result['total_pages'], 7)
        self.assertEqual(len(result['merged_files']), 2)

        # 验证合并后的CBZ文件
        self.assertTrue(FileUtils.is_valid_cbz_file(str(output_path)))

        # 验证合并后的内容
        info = FileUtils.extract_cbz_info(str(output_path))
        self.assertEqual(info['page_count'], 7)

        # 检查页面顺序
        image_files = info['image_files']
        self.assertEqual(len(image_files), 7)
        # 前3个应该来自volume_1，后4个来自volume_2
        for i in range(3):
            self.assertTrue(image_files[i].endswith(f"{i+1:04d}.jpg"))

    def test_progress_callback(self):
        """测试进度回调"""
        progress_calls = []

        def progress_callback(progress: MergeProgress):
            progress_calls.append((progress.current_progress, progress.total_progress))

        self.merger.set_progress_callback(progress_callback)

        # 创建测试文件
        file1 = self.create_test_cbz("volume_1", 2)
        file2 = self.create_test_cbz("volume_2", 2)
        output_path = Path(self.temp_dir) / "progress_test.cbz"

        # 合并文件
        result = self.merger.merge_cbz_files([file1, file2], str(output_path))

        # 验证进度回调被调用
        self.assertTrue(len(progress_calls) > 0)
        self.assertTrue(result['success'])

    def test_invalid_file_handling(self):
        """测试无效文件处理"""
        # 创建无效文件
        invalid_file = Path(self.temp_dir) / "invalid.cbz"
        invalid_file.write_text("This is not a valid CBZ file")

        # 测试验证
        result = self.merger.validate_cbz_files([str(invalid_file)])
        self.assertEqual(len(result['valid_files']), 0)
        self.assertEqual(len(result['invalid_files']), 1)


class TestFileUtils(unittest.TestCase):
    """文件工具测试类"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp(prefix='comicmanager_fileutils_test_')

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_valid_cbz_file(self):
        """测试CBZ文件有效性检查"""
        # 创建有效的CBZ文件
        cbz_path = Path(self.temp_dir) / "valid.cbz"
        with zipfile.ZipFile(cbz_path, 'w') as zf:
            zf.writestr("test.jpg", b"test image content")

        # 测试有效文件
        self.assertTrue(FileUtils.is_valid_cbz_file(str(cbz_path)))

        # 测试无效文件
        invalid_file = Path(self.temp_dir) / "invalid.txt"
        invalid_file.write_text("not a zip file")
        self.assertFalse(FileUtils.is_valid_cbz_file(str(invalid_file)))

        # 测试不存在的文件
        self.assertFalse(FileUtils.is_valid_cbz_file("nonexistent.cbz"))

    def test_get_file_size_str(self):
        """测试文件大小字符串格式化"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_bytes(b"x" * 1024)  # 1KB

        size_str = FileUtils.get_file_size_str(str(test_file))
        self.assertIn("KB", size_str)

        # 测试不存在的文件
        self.assertEqual(FileUtils.get_file_size_str("nonexistent.txt"), "Unknown")

    def test_sanitize_filename(self):
        """测试文件名清理"""
        # 测试非法字符
        self.assertEqual(FileUtils.sanitize_filename("file<>name"), "file__name")
        self.assertEqual(FileUtils.sanitize_filename("file:name"), "file_name")

        # 测试空文件名
        self.assertNotEqual(FileUtils.sanitize_filename(""), "")
        self.assertEqual(FileUtils.sanitize_filename("   . "), "unnamed")

    def test_get_unique_filename(self):
        """测试获取唯一文件名"""
        # 创建一个文件
        existing_file = Path(self.temp_dir) / "test.cbz"
        existing_file.touch()

        # 测试获取唯一文件名
        unique = FileUtils.get_unique_filename(str(self.temp_dir), "test", ".cbz")
        self.assertEqual(unique, "test_1.cbz")

        # 测试不存在的文件名
        unique2 = FileUtils.get_unique_filename(str(self.temp_dir), "nonexistent", ".cbz")
        self.assertEqual(unique2, "nonexistent.cbz")


class TestInputValidator(unittest.TestCase):
    """输入验证测试类"""

    def test_validate_filename(self):
        """测试文件名验证"""
        # 测试有效文件名
        valid, error = InputValidator.validate_filename("test_file.cbz")
        self.assertTrue(valid)
        self.assertIsNone(error)

        # 测试非法字符
        valid, error = InputValidator.validate_filename("test<>file.cbz")
        self.assertFalse(valid)
        self.assertIsNotNone(error)

        # 测试空文件名
        valid, error = InputValidator.validate_filename("")
        self.assertFalse(valid)
        self.assertIsNotNone(error)

        # 测试保留名称
        valid, error = InputValidator.validate_filename("CON.cbz")
        self.assertFalse(valid)
        self.assertIsNotNone(error)

    def test_validate_numeric_input(self):
        """测试数值输入验证"""
        # 测试有效数值
        valid, value = InputValidator.validate_numeric_input("100")
        self.assertTrue(valid)
        self.assertEqual(value, 100)

        # 测试范围限制
        valid, value = InputValidator.validate_numeric_input("50", min_val=100)
        self.assertFalse(valid)
        self.assertIsNone(value)

        valid, value = InputValidator.validate_numeric_input("150", max_val=100)
        self.assertFalse(valid)
        self.assertIsNone(value)

        # 测试无效输入
        valid, value = InputValidator.validate_numeric_input("abc")
        self.assertFalse(valid)
        self.assertIsNone(value)


def run_manual_tests():
    """手动测试指导"""
    print("=== ComicManager 手动测试指导 ===")
    print()

    print("1. 基础功能测试:")
    print("   - 启动程序: uv run python -m comicmanager.main")
    print("   - 使用example文件夹中的两个CBZ文件")
    print("   - 测试添加、删除、清空文件列表功能")
    print("   - 测试文件排序功能（上移、下移、置顶、置底）")
    print("   - 测试拖拽排序功能")
    print()

    print("2. 合并功能测试:")
    print("   - 选择example文件夹中的两个CBZ文件")
    print("   - 设置输出文件名")
    print("   - 点击'开始合并'按钮")
    print("   - 验证合并后的CBZ文件是否包含所有页面")
    print("   - 验证页面顺序是否正确")
    print()

    print("3. 错误处理测试:")
    print("   - 添加非CBZ文件，验证错误提示")
    print("   - 重复添加同一文件，验证重复提示")
    print("   - 设置无效输出路径，验证错误提示")
    print("   - 在合并过程中取消操作，验证程序响应")
    print()

    print("4. 设置功能测试:")
    print("   - 打开设置窗口，测试各项设置")
    print("   - 修改主题设置，验证界面变化")
    print("   - 修改默认输出目录，验证设置保存")
    print()

    print("5. 键盘快捷键测试:")
    print("   - Ctrl+O: 添加文件")
    print("   - Ctrl+A: 全选")
    print("   - Delete: 删除选中")
    print("   - Ctrl+Up/Down: 移动选中项")
    print("   - Ctrl+Home/End: 移至顶部/底部")
    print()

    print("6. 性能测试:")
    print("   - 使用大文件测试合并性能")
    print("   - 测试内存使用情况")
    print("   - 验证临时文件清理")
    print()

    print("7. 边界情况测试:")
    print("   - 空文件列表时点击合并")
    print("   - 单个文件时点击合并")
    print("   - 很长的文件名")
    print("   - 特殊字符的文件名")
    print()

    print("自动测试命令:")
    print("  运行所有测试: python -m pytest comicmanager/tests/")
    print("  运行特定测试: python -m pytest comicmanager/tests/test_merger.py::TestCBZMerger::test_merge_cbz_files")


if __name__ == "__main__":
    # 运行测试
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        run_manual_tests()
    else:
        # 运行单元测试
        unittest.main(verbosity=2)