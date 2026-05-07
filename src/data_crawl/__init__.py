# src/data_crawl/__init__.py
"""网页抓取模块"""

# Task 1: 仅导出 utils 模块，后续任务逐步添加
from .utils import (
    random_delay,
    sanitize_filename,
    load_state,
    save_state,
)

__all__ = [
    "random_delay",
    "sanitize_filename",
    "load_state",
    "save_state",
]
