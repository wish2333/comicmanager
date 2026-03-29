"""YAML-based application configuration management."""

import copy
from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path.home() / ".comicmanager"
_CONFIG_FILE = _CONFIG_DIR / "config.yaml"

_DEFAULT_CONFIG: dict[str, Any] = {
    "app": {
        "name": "ComicManager Neo",
        "version": "1.0.0",
        "language": "zh-CN",
    },
    "output": {
        "default_dir": str(Path.home()),
        "auto_increment": True,
        "preserve_metadata": True,
    },
    "zip_extraction": {
        "default_formats": ["jpg", "jpeg", "png", "webp"],
        "max_image_size_mb": 100,
    },
    "ui": {
        "theme": "light",
        "window": {
            "width": 1000,
            "height": 700,
            "min_width": 800,
            "min_height": 600,
        },
    },
    "recent": {
        "max_count": 10,
        "files": [],
    },
    "server": {
        "host": "127.0.0.1",
        "port": 0,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_config() -> dict[str, Any]:
    """Load configuration from disk. Returns merged config (defaults + user)."""
    try:
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            return _deep_merge(_DEFAULT_CONFIG, user_config)
    except Exception:
        pass
    return copy.deepcopy(_DEFAULT_CONFIG)


def save_config(config: dict[str, Any]) -> None:
    """Persist configuration to YAML file."""
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except Exception:
        pass


def get_config() -> dict[str, Any]:
    """Load-or-get cached config (convenience wrapper)."""
    return load_config()


def update_config(updates: dict[str, Any]) -> dict[str, Any]:
    """Apply *updates* to the current config and persist. Returns new config."""
    current = load_config()
    merged = _deep_merge(current, updates)
    save_config(merged)
    return merged
