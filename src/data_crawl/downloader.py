# src/data_crawl/downloader.py
"""图片下载器"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    import aiohttp
    import aiofiles
except ImportError:
    aiohttp = None
    aiofiles = None

logger = logging.getLogger(__name__)


async def download_single_image(
    url: str,
    save_path: str,
    timeout: int = 30,
    session: Optional[object] = None,
    referer: Optional[str] = None,
) -> bool:
    """
    下载单张图片
    
    Args:
        url: 图片 URL
        save_path: 保存路径
        timeout: 超时时间（秒）
        session: aiohttp ClientSession（复用连接）
        referer: Referer 头（防盗链）
    
    Returns:
        是否成功
    """
    if aiohttp is None:
        raise ImportError("aiohttp not installed. Run: pip install aiohttp aiofiles")
    
    try:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        headers = {}
        if referer:
            headers['Referer'] = referer
        
        async def do_download(sess):
            async with sess.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as response:
                if response.status != 200:
                    return False
                
                content = await response.read()
                
                if aiofiles:
                    async with aiofiles.open(save_path, 'wb') as f:
                        await f.write(content)
                else:
                    with open(save_path, 'wb') as f:
                        f.write(content)
                
                return True
        
        if session:
            return await do_download(session)
        else:
            async with aiohttp.ClientSession() as sess:
                return await do_download(sess)
                
    except Exception as e:
        logger.error(f"下载图片失败 {url}: {e}")
        return False


async def download_images(
    image_urls: List[str],
    output_dir: str,
    article_title: str = "",
    max_concurrent: int = 3,
    referer: Optional[str] = None,
) -> Dict[str, str]:
    """
    批量下载图片
    
    Args:
        image_urls: 图片 URL 列表
        output_dir: 输出目录
        article_title: 文章标题（用于子目录名）
        max_concurrent: 最大并发数
        referer: Referer 头（防盗链）
    
    Returns:
        URL 到本地路径的映射
    """
    if not image_urls:
        return {}
    
    if article_title:
        from .utils import sanitize_filename
        subdir = sanitize_filename(article_title)
        output_dir = os.path.join(output_dir, subdir)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_with_semaphore(url: str, index: int, session):
        async with semaphore:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            ext = 'jpg'
            if path.endswith('.png'):
                ext = 'png'
            elif path.endswith('.gif'):
                ext = 'gif'
            elif path.endswith('.webp'):
                ext = 'webp'
            elif path.endswith('.jpeg') or path.endswith('.jpg'):
                ext = 'jpg'
            
            filename = f"img_{index:03d}.{ext}"
            save_path = os.path.join(output_dir, filename)
            
            success = await download_single_image(url, save_path, session=session, referer=referer)
            
            if success:
                return url, save_path
            return url, None
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            download_with_semaphore(url, i + 1, session)
            for i, url in enumerate(image_urls)
        ]
        
        download_results = await asyncio.gather(*tasks)
    
    for url, local_path in download_results:
        if local_path:
            results[url] = local_path
    
    return results
