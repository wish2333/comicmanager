"""
配置管理模块
处理应用程序配置和设置
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """应用程序配置管理类"""

    def __init__(self):
        self.config_dir = Path.home() / '.comicmanager'
        self.config_file = self.config_dir / 'config.json'
        self.default_config = {
            'last_output_dir': str(Path.home()),
            'auto_increment': True,
            'backup_original': False,
            'theme': 'default',
            'window_geometry': None,
            'remember_files': True,
            'recent_files': []
        }
        self._config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                self._config = {**self.default_config, **loaded_config}
            else:
                self._config = self.default_config.copy()
                self.save_config()
            return self._config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self._config = self.default_config.copy()
            return self._config

    def save_config(self) -> None:
        """保存配置文件"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if not self._config:
            self.load_config()
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        if not self._config:
            self.load_config()
        self._config[key] = value
        self.save_config()

    def add_recent_file(self, file_path: str) -> None:
        """添加最近使用的文件"""
        recent_files = self.get('recent_files', [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        # 只保留最近10个文件
        recent_files = recent_files[:10]
        self.set('recent_files', recent_files)