# src/data_crawl/api.py
"""同步 API 适配层，供 Skill 调用"""

import asyncio
import os
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .browser import BrowserManager
from .downloader import download_images
from .extractor import ArticleData, convert_to_markdown, extract_article, extract_list_links
from .selectors import Platform, detect_platform, is_article_page, is_list_page
from .utils import sanitize_filename


@dataclass
class CrawlResult:
    """抓取结果"""
    success: bool
    files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    article_count: int = 0


def _run_async(coro):
    """运行异步协程"""
    warnings.filterwarnings("ignore", category=ResourceWarning)
    
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        return asyncio.run(coro)
    except KeyboardInterrupt:
        return None
    finally:
        import gc
        gc.collect()


async def _crawl_single_article(
    url: str,
    output_dir: str,
    browser_manager: Optional[BrowserManager] = None,
    download_imgs: bool = False,
    images_dir: Optional[str] = None,
) -> tuple[bool, Optional[str], Optional[str]]:
    """
    抓取单篇文章
    
    Returns:
        (success, file_path, error_message)
    """
    platform = detect_platform(url)
    
    should_close = False
    if browser_manager is None:
        browser_manager = BrowserManager()
        await browser_manager.create_context()
        should_close = True
    
    page = await browser_manager.new_page()
    
    try:
        await page.goto(url, wait_until='networkidle')
        
        article = await extract_article(page, platform)
        
        if article is None:
            return False, None, "提取文章失败"
        
        if download_imgs and article.images:
            img_dir = images_dir or os.path.join(output_dir, "images")
            local_paths = await download_images(
                article.images,
                img_dir,
                article.title,
                referer=url,
            )
            for orig_url, local_path in local_paths.items():
                rel_path = os.path.relpath(local_path, output_dir)
                article.content = article.content.replace(orig_url, rel_path)
        
        markdown = convert_to_markdown(article)
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        md_filename = f"{sanitize_filename(article.title)}.md"
        md_path = os.path.join(output_dir, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return True, md_path, None
        
    except Exception as e:
        return False, None, str(e)
    finally:
        await page.close()
        if should_close:
            await browser_manager.close()


async def _crawl_list_page(
    url: str,
    output_dir: str,
    download_imgs: bool = False,
    images_dir: Optional[str] = None,
    limit: Optional[int] = None,
    delay: float = 2.0,
) -> CrawlResult:
    """抓取列表页"""
    from .utils import random_delay
    
    platform = detect_platform(url)
    
    browser_manager = BrowserManager()
    await browser_manager.create_context()
    
    files = []
    errors = []
    
    try:
        page = await browser_manager.new_page()
        
        await page.goto(url, wait_until='networkidle')
        
        links = await extract_list_links(page, platform)
        
        if limit:
            links = links[:limit]
        
        await page.close()
        
        for i, link in enumerate(links, 1):
            if i > 1:
                random_delay(max(0.5, delay), delay + 3)
            
            success, file_path, error = await _crawl_single_article(
                link,
                output_dir,
                browser_manager=browser_manager,
                download_imgs=download_imgs,
                images_dir=images_dir,
            )
            
            if success and file_path:
                files.append(file_path)
            elif error:
                errors.append(f"{link}: {error}")
        
        return CrawlResult(
            success=len(files) > 0,
            files=files,
            error="\n".join(errors) if errors else None,
            article_count=len(files),
        )
        
    finally:
        await browser_manager.close()


async def _crawl_article(url: str, output_dir: str, download_imgs: bool) -> CrawlResult:
    """抓取单篇文章的通用逻辑"""
    success, file_path, error = await _crawl_single_article(
        url, output_dir, download_imgs=download_imgs
    )
    return CrawlResult(
        success=success,
        files=[file_path] if file_path else [],
        error=error,
        article_count=1 if success else 0,
    )


def crawl_url(
    url: str,
    output_dir: str = "misc/",
    download_images: bool = False,
    limit: Optional[int] = None,
    delay: float = 2.0,
) -> CrawlResult:
    """
    抓取 URL（单篇文章或列表页）
    
    Args:
        url: 文章页或列表页 URL
        output_dir: 输出目录
        download_images: 是否下载图片到本地
        limit: 列表页最大抓取数
        delay: 请求延迟（秒）
    
    Returns:
        CrawlResult 抓取结果
    """
    platform = detect_platform(url)
    
    if is_article_page(url, platform):
        return _run_async(_crawl_article(url, output_dir, download_images))
    
    elif is_list_page(url, platform):
        return _run_async(_crawl_list_page(
            url, output_dir,
            download_imgs=download_images,
            limit=limit,
            delay=delay,
        ))
    
    else:
        return _run_async(_crawl_article(url, output_dir, download_images))
