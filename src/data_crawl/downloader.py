# src/data_crawl/downloader.py
"""图片下载器"""

import asyncio
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


async def download_single_image(
    url: str,
    save_path: str,
    timeout: int = 30,
) -> bool:
    """
    下载单张图片
    
    Args:
        url: 图片 URL
        save_path: 保存路径
        timeout: 超时时间（秒）
    
    Returns:
        是否成功
    """
    if aiohttp is None:
        raise ImportError("aiohttp not installed. Run: pip install aiohttp aiofiles")
    
    try:
        # 确保目录存在
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status != 200:
                    return False
                
                content = await response.read()
                
                # 异步写入文件
                if aiofiles:
                    async with aiofiles.open(save_path, 'wb') as f:
                        await f.write(content)
                else:
                    with open(save_path, 'wb') as f:
                        f.write(content)
                
                return True
    except Exception as e:
        print(f"[ERROR] 下载图片失败 {url}: {e}")
        return False


async def download_images(
    image_urls: List[str],
    output_dir: str,
    article_title: str = "",
    max_concurrent: int = 3,
) -> Dict[str, str]:
    """
    批量下载图片
    
    Args:
        image_urls: 图片 URL 列表
        output_dir: 输出目录
        article_title: 文章标题（用于子目录名）
        max_concurrent: 最大并发数
    
    Returns:
        URL 到本地路径的映射
    """
    if not image_urls:
        return {}
    
    # 创建子目录
    if article_title:
        from .utils import sanitize_filename
        subdir = sanitize_filename(article_title)
        output_dir = os.path.join(output_dir, subdir)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_with_semaphore(url: str, index: int):
        async with semaphore:
            # 从 URL 提取扩展名
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if '.png' in path:
                ext = 'png'
            elif '.gif' in path:
                ext = 'gif'
            elif '.webp' in path:
                ext = 'webp'
            elif '.jpeg' in path or '.jpg' in path:
                ext = 'jpg'
            else:
                ext = 'jpg'  # 默认
            
            filename = f"img_{index:03d}.{ext}"
            save_path = os.path.join(output_dir, filename)
            
            success = await download_single_image(url, save_path)
            
            if success:
                return url, save_path
            return url, None
    
    # 并发下载
    tasks = [
        download_with_semaphore(url, i + 1)
        for i, url in enumerate(image_urls)
    ]
    
    download_results = await asyncio.gather(*tasks)
    
    for url, local_path in download_results:
        if local_path:
            results[url] = local_path
    
    return results
