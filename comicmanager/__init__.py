"""
ComicManager - CBZ文件合并工具
支持多个CBZ文件按自定义顺序合并的Python GUI应用程序
"""

__version__ = "0.1.0"
__author__ = "ComicManager Team"

from .core.cbz_merger import CBZMerger
from .gui.main_window import MainWindow

__all__ = ['CBZMerger', 'MainWindow']