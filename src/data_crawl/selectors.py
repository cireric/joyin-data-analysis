# src/data_crawl/selectors.py
"""各平台 CSS 选择器配置"""

from enum import Enum
from typing import Dict, Any, Optional


class Platform(Enum):
    """支持的平台"""
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    JIANSHU = "jianshu"
    GENERIC = "generic"


PLATFORM_CONFIGS: Dict[Platform, Dict[str, Any]] = {
    Platform.WECHAT: {
        "name": "微信公众号",
        "article_patterns": [r"mp\.weixin\.qq\.com/s/"],
        "list_patterns": [r"mp\.weixin\.qq\.com/mp/profile_ext"],
        "article_selector": "#js_content",
        "title_selector": "#activity-name",
        "author_selector": "#js_name",
        "date_selector": "#publish_time",
        "list_link_selector": "a[href*='/s/']",
        "needs_scroll": True,
    },
    Platform.ZHIHU: {
        "name": "知乎专栏",
        "article_patterns": [r"zhuanlan\.zhihu\.com/p/"],
        "list_patterns": [r"zhuanlan\.zhihu\.com/p/\?page=", r"zhihu\.com/people/.*/posts"],
        "article_selector": ".Post-RichText, .RichText",
        "title_selector": ".Post-Title, .ContentItem-title",
        "author_selector": ".AuthorInfo-name",
        "date_selector": ".ContentItem-time",
        "list_link_selector": "a[href*='/p/']",
        "needs_scroll": False,
    },
    Platform.JIANSHU: {
        "name": "简书",
        "article_patterns": [r"jianshu\.com/p/"],
        "list_patterns": [r"jianshu\.com/u/"],
        "article_selector": "article, .article",
        "title_selector": "h1.title, .title",
        "author_selector": ".author .name",
        "date_selector": ".publish-time",
        "list_link_selector": "a[href*='/p/']",
        "needs_scroll": True,
    },
    Platform.GENERIC: {
        "name": "通用网页",
        "article_patterns": [],
        "list_patterns": [],
        "article_selector": "article, main, .content, .post, .entry",
        "title_selector": "h1, .title, .post-title",
        "author_selector": ".author, .byline",
        "date_selector": ".date, .time, .published",
        "list_link_selector": "a",
        "needs_scroll": False,
    },
}


def detect_platform(url: str) -> Platform:
    """
    根据 URL 检测平台
    
    Args:
        url: 网页 URL
    
    Returns:
        平台枚举值
    """
    import re
    
    for platform, config in PLATFORM_CONFIGS.items():
        patterns = config.get("article_patterns", []) + config.get("list_patterns", [])
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    
    return Platform.GENERIC


def get_platform_config(platform: Platform) -> Dict[str, Any]:
    """
    获取平台配置
    
    Args:
        platform: 平台枚举值
    
    Returns:
        平台配置字典
    """
    return PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS[Platform.GENERIC])


def is_article_page(url: str, platform: Optional[Platform] = None) -> bool:
    """
    判断是否为文章页
    
    Args:
        url: 网页 URL
        platform: 平台（可选，不传则自动检测）
    
    Returns:
        是否为文章页
    """
    import re
    
    if platform is None:
        platform = detect_platform(url)
    
    config = get_platform_config(platform)
    patterns = config.get("article_patterns", [])
    
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    
    return False


def is_list_page(url: str, platform: Optional[Platform] = None) -> bool:
    """
    判断是否为列表页
    
    Args:
        url: 网页 URL
        platform: 平台（可选，不传则自动检测）
    
    Returns:
        是否为列表页
    """
    import re
    
    if platform is None:
        platform = detect_platform(url)
    
    config = get_platform_config(platform)
    patterns = config.get("list_patterns", [])
    
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    
    return False
