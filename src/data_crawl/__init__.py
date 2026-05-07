# src/data_crawl/__init__.py
"""网页抓取模块"""

# Task 1: 仅导出 utils 模块，后续任务逐步添加
from .utils import (
    random_delay,
    sanitize_filename,
    load_state,
    save_state,
)

# Task 2: 导出浏览器管理器
from .browser import BrowserManager

# Task 3: 导出平台选择器
from .selectors import get_platform_config, detect_platform, Platform, is_article_page, is_list_page

# Task 4: 导出内容提取器
from .extractor import extract_article, extract_list_links, convert_to_markdown, ArticleData

# Task 5: 导出图片下载器
from .downloader import download_images, download_single_image

__all__ = [
    "random_delay",
    "sanitize_filename",
    "load_state",
    "save_state",
    "BrowserManager",
    "Platform",
    "detect_platform",
    "is_article_page",
    "is_list_page",
    "ArticleData",
    "extract_article",
    "extract_list_links",
    "convert_to_markdown",
    "download_images",
    "download_single_image",
]
