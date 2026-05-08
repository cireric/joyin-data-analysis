# src/data_crawl/extractor.py
"""内容提取器：文章提取、列表提取、Markdown 转换"""

import asyncio
import logging
import random
import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode

from .selectors import Platform, get_platform_config, is_article_page

logger = logging.getLogger(__name__)


def clean_image_url(url: str) -> str:
    """
    清理图片 URL，移除不必要的参数
    
    Args:
        url: 原始 URL
    
    Returns:
        清理后的 URL
    """
    if not url:
        return url
    
    url = url.replace('&amp;', '&')
    
    try:
        parsed = urlparse(url)
        
        keep_params = []
        if parsed.query:
            params = parse_qs(parsed.query)
            for key in ['wx_fmt', 'tp']:
                if key in params:
                    keep_params.append((key, params[key][0]))
        
        if keep_params:
            new_query = urlencode(keep_params)
        else:
            new_query = ''
        
        clean_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            ''
        ))
        
        return clean_url
    except Exception:
        return url.split('?')[0].split('#')[0]


def remove_noise_elements(content: str) -> str:
    """
    移除内容中的噪音元素（广告、推荐等）
    
    Args:
        content: HTML 内容
    
    Returns:
        清理后的内容
    """
    noise_patterns = [
        (r'<div[^>]*class="[^"]*qr-code[^"]*"[^>]*>.*?</div>', ''),
        (r'<div[^>]*class="[^"]*recommend[^"]*"[^>]*>.*?</div>', ''),
        (r'<div[^>]*class="[^"]*ad[^"]*"[^>]*>.*?</div>', ''),
        (r'<div[^>]*id="[^"]*ad[^"]*"[^>]*>.*?</div>', ''),
        (r'<section[^>]*class="[^"]*mp_profile_popup[^"]*"[^>]*>.*?</section>', ''),
        (r'<section[^>]*class="[^"]*js_ad[^"]*"[^>]*>.*?</section>', ''),
        (r'<a[^>]*class="[^"]*appmsg_card[^"]*"[^>]*>.*?</a>', ''),
    ]
    
    for pattern, replacement in noise_patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
    
    return content


@dataclass
class ArticleData:
    """文章数据"""
    title: str
    author: str
    date: str
    url: str
    content: str
    images: List[str] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []


async def extract_article(page, platform: Platform) -> Optional[ArticleData]:
    """
    提取文章内容
    
    Args:
        page: Playwright 页面对象
        platform: 平台
    
    Returns:
        文章数据，失败返回 None
    """
    try:
        config = get_platform_config(platform)
        
        await page.evaluate("""
            async () => {
                const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                const scrollHeight = document.documentElement.scrollHeight;
                const viewportHeight = window.innerHeight;
                const steps = Math.ceil(scrollHeight / viewportHeight);
                
                for (let i = 0; i < steps; i++) {
                    window.scrollTo(0, viewportHeight * i);
                    await delay(300);
                }
                window.scrollTo(0, 0);
            }
        """)
        
        await asyncio.sleep(0.5)
        
        title = ""
        title_selector = config.get("title_selector")
        if title_selector:
            title_elem = await page.query_selector(title_selector)
            if title_elem:
                title = await title_elem.inner_text()
        if not title:
            title = await page.title()
        
        author = ""
        author_selector = config.get("author_selector")
        if author_selector:
            author_elem = await page.query_selector(author_selector)
            if author_elem:
                author = await author_elem.inner_text()
        
        date = ""
        date_selector = config.get("date_selector")
        if date_selector:
            date_elem = await page.query_selector(date_selector)
            if date_elem:
                date = await date_elem.inner_text()
        
        content = ""
        article_selector = config.get("article_selector")
        if article_selector:
            content_elem = await page.query_selector(article_selector)
            if content_elem:
                content = await content_elem.inner_html()
        
        images = []
        img_selectors = []
        if article_selector:
            for sel in article_selector.split(","):
                img_selectors.append(f"{sel.strip()} img")
        else:
            img_selectors = ["img"]
        
        for img_sel in img_selectors:
            img_elements = await page.query_selector_all(img_sel)
            for img in img_elements:
                src = await img.get_attribute("data-src") or await img.get_attribute("src")
                if src and not src.startswith("data:"):
                    src = clean_image_url(src)
                    if src and src not in images:
                        images.append(src)
        
        return ArticleData(
            title=title.strip(),
            author=author.strip(),
            date=date.strip(),
            url=page.url,
            content=content,
            images=images,
        )
    except Exception as e:
        logger.error(f"提取文章失败: {e}")
        return None


async def extract_list_links(page, platform: Platform, scroll: bool = True) -> List[str]:
    """
    提取列表页的文章链接
    
    Args:
        page: Playwright 页面对象
        platform: 平台
        scroll: 是否滚动加载更多
    
    Returns:
        文章链接列表
    """
    config = get_platform_config(platform)
    link_selector = config.get("list_link_selector", "a")
    links = set()
    
    if scroll and config.get("needs_scroll", False):
        prev_count = 0
        no_change_count = 0
        
        while no_change_count < 3:
            scroll_distance = random.randint(300, 800)
            await page.evaluate(f'window.scrollBy(0, {scroll_distance})')
            
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            elements = await page.query_selector_all(link_selector)
            for elem in elements:
                href = await elem.get_attribute("href")
                if href:
                    full_url = urljoin(page.url, href)
                    links.add(full_url)
            
            if len(links) == prev_count:
                no_change_count += 1
            else:
                no_change_count = 0
            prev_count = len(links)
    else:
        elements = await page.query_selector_all(link_selector)
        for elem in elements:
            href = await elem.get_attribute("href")
            if href:
                full_url = urljoin(page.url, href)
                links.add(full_url)
    
    article_links = [link for link in links if is_article_page(link, platform)]
    
    return list(set(article_links))


def convert_img_tag(img_tag: str) -> str:
    """
    将 img 标签转换为 Markdown 格式
    
    Args:
        img_tag: img 标签字符串
    
    Returns:
        Markdown 格式的图片
    """
    src_match = re.search(r'(?:data-)?src=["\']([^"\']+)["\']', img_tag)
    alt_match = re.search(r'alt=["\']([^"\']*)["\']', img_tag)
    
    if not src_match:
        return ''
    
    src = src_match.group(1)
    alt = alt_match.group(1) if alt_match else 'image'
    
    src = clean_image_url(src)
    
    return f'\n![{alt}]({src}){{width="600"}}\n'


def convert_to_markdown(article: ArticleData, image_dir: Optional[str] = None) -> str:
    """
    将文章转换为 Markdown 格式
    
    Args:
        article: 文章数据
        image_dir: 图片目录（用于本地图片路径）
    
    Returns:
        Markdown 文本
    """
    lines = []
    
    lines.append(f"# {article.title}")
    lines.append("")
    
    if article.author:
        lines.append(f"**作者：** {article.author}")
    if article.date:
        lines.append(f"**发布时间：** {article.date}")
    lines.append(f"**来源：** {article.url}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    content = article.content
    
    content = remove_noise_elements(content)
    
    content = re.sub(r'<br\s*/?>', '\n', content)
    content = re.sub(r'<p[^>]*>', '', content)
    content = re.sub(r'</p>', '\n\n', content)
    content = re.sub(r'<section[^>]*>', '', content)
    content = re.sub(r'</section>', '\n', content)
    content = re.sub(r'<strong[^>]*>((?:(?!<img).)*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<b[^>]*>((?:(?!<img).)*?)</b>', r'**\1**', content, flags=re.DOTALL)
    content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', content, flags=re.DOTALL)
    content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n\n', content, flags=re.DOTALL)
    content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n\n', content, flags=re.DOTALL)
    content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n\n', content, flags=re.DOTALL)
    
    content = re.sub(r'<img[^>]*>', lambda m: convert_img_tag(m.group(0)), content)
    
    content = re.sub(r'!\[.*?\]\(data:image[^)]+\)', '', content)
    
    content = re.sub(r'&nbsp;', ' ', content)
    content = re.sub(r'&amp;', '&', content)
    content = re.sub(r'&lt;', '<', content)
    content = re.sub(r'&gt;', '>', content)
    content = re.sub(r'&quot;', '"', content)
    
    content = re.sub(r'<[^>]+>', '', content)
    
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    lines.append(content)
    
    return '\n'.join(lines)
