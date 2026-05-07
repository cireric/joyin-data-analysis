# src/data_crawl/__init__.py
"""网页抓取模块"""

# Task 1: 仅导出 utils 模块，后续任务逐步添加
from .utils import (
    random_delay,
    sanitize_filename,
    load_state,
    save_state,
)

# Task 3: 导出平台选择器
from .selectors import get_platform_config, detect_platform, Platform, is_article_page, is_list_page

__all__ = [
    "random_delay",
    "sanitize_filename",
    "load_state",
    "save_state",
    "Platform",
    "is_article_page",
    "is_list_page",
]
