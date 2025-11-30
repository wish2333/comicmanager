@staticmethod
    def is_valid_zip_file(file_path: str) -> bool:
        """检查是否为有效的ZIP文件（包含图片）"""
        try:
            # 标准化路径
            import os
            file_path = os.path.normpath(file_path)

            path = Path(file_path)
            if not path.exists() or not path.is_file():
                print(f"ZIP验证失败: 文件不存在 - {file_path}")
                return False

            # 检查文件扩展名
            if path.suffix.lower() != '.zip':
                print(f"ZIP验证失败: 扩展名错误 - {path.suffix}")
                return False

            # 检查是否为有效的ZIP文件
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 检查是否包含图片文件
                image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
                has_images = False
                image_count = 0

                for file_name in zf.namelist():
                    # 跳过目录
                    if file_name.endswith('/'):
                        continue

                    # 安全检查：防止路径遍历攻击
                    if '..' in file_name or file_name.startswith('/'):
                        continue

                    file_ext = Path(file_name).suffix.lower()
                    if file_ext in image_extensions:
                        has_images = True
                        image_count += 1

                if has_images:
                    print(f"ZIP验证成功: {file_path} (包含 {image_count} 张图片)")
                    return True
                else:
                    print(f"ZIP验证失败: 不包含支持的图片 - {file_path}")
                    return False
        except zipfile.BadZipFile:
            print(f"ZIP验证失败: 损坏的ZIP文件 - {file_path}")
            return False
        except PermissionError:
            print(f"ZIP验证失败: 权限不足 - {file_path}")
            return False
        except UnicodeDecodeError:
            print(f"ZIP验证失败: 文件名编码问题 - {file_path}")
            return False
        except Exception as e:
            print(f"ZIP验证失败: 未知错误 - {file_path}: {e}")
            return False