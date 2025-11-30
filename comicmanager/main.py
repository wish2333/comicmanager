"""
ComicManager主程序入口
启动CBZ文件合并工具
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径，以便导入模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from .gui.main_window import MainWindow
    from .core.config import Config
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from comicmanager.gui.main_window import MainWindow
        from comicmanager.core.config import Config
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有必要的依赖包")
        sys.exit(1)


def main():
    """主函数"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 10):
            print("错误: 需要Python 3.10或更高版本")
            sys.exit(1)

        # 加载配置
        config = Config()
        config.load_config()

        # 创建并运行主窗口
        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main_cli():
    """命令行入口（用于packaging）"""
    main()


if __name__ == "__main__":
    main()