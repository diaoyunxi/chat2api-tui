#!/usr/bin/env python3
# core/config.py
"""统一配置管理，从 config.yml 读取配置"""
import os
import yaml
from typing import Any, Dict

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")
DEFAULT_CONFIG = {
    "base_url": "http://127.0.0.1:8080/v1",
    "api_key": "",
    "default_model": "deepseek-v4-flash",
    "supported_models": ["deepseek-v4-flash", "deepseek-v4-pro"],
    "max_iterations": 10,
}

_config: Dict[str, Any] = None

def load_config() -> Dict[str, Any]:
    """加载配置文件，如果不存在则使用默认值（并发出警告）"""
    global _config
    if _config is not None:
        return _config

    if not os.path.exists(CONFIG_PATH):
        print("⚠️  未找到 config.yml，使用默认配置（建议复制 config.example.yml 并填写）")
        _config = DEFAULT_CONFIG.copy()
        return _config

    # 限制配置文件大小防止 DoS (CWE-400)
    MAX_CONFIG_SIZE = 1 * 1024 * 1024  # 1MB
    if os.path.getsize(CONFIG_PATH) > MAX_CONFIG_SIZE:
        raise ValueError(f"配置文件过大: {os.path.getsize(CONFIG_PATH)} bytes > {MAX_CONFIG_SIZE}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    # 合并默认值
    merged = DEFAULT_CONFIG.copy()
    merged.update(cfg)
    _config = merged
    return _config

def get(key: str, default=None):
    """获取配置项"""
    return load_config().get(key, default)
