#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""URL to Markdown 命令行工具"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_crawl import (
    random_delay,
    sanitize_filename,
    load_state,
    save_state,
    BrowserManager,
    Platform,
    detect_platform,
    is_article_page,
    is_list_page,
    extract_article,
    extract_list_links,
    convert_to_markdown,
    download_images,
)


async def crawl_single_article(
    url: str,
    output_dir: str,
    filename: Optional[str] = None,
    download_imgs: bool = False,
    images_dir: Optional[str] = None,
    browser_manager: Optional[BrowserManager] = None,
) -> bool:
    """
    抓取单篇文章
    
    Args:
        url: 文章 URL
        output_dir: 输出目录
        filename: 文件名
        download_imgs: 是否下载图片
        images_dir: 图片目录
        browser_manager: 浏览器管理器
    
    Returns:
        是否成功
    """
    platform = detect_platform(url)
    print(f"[INFO] 检测到文章页 ({platform.value})")
    
    # 创建浏览器
    if browser_manager is None:
        browser_manager = BrowserManager()
        await browser_manager.create_context()
    
    page = await browser_manager.new_page()
    
    try:
        print(f"[INFO] 正在抓取: {url}")
        await page.goto(url, wait_until='networkidle')
        
        article = await extract_article(page, platform)
        
        if article is None:
            print(f"[ERROR] 提取文章失败")
            return False
        
        print(f"[INFO] 正在抓取: {article.title}")
        
        # 下载图片
        if download_imgs and article.images:
            img_dir = images_dir or os.path.join(output_dir, "images")
            print(f"[INFO] 下载 {len(article.images)} 张图片...")
            local_paths = await download_images(
                article.images,
                img_dir,
                article.title
            )
            # 更新图片路径
            for orig_url, local_path in local_paths.items():
                rel_path = os.path.relpath(local_path, output_dir)
                article.content = article.content.replace(orig_url, rel_path)
        
        # 转换为 Markdown
        markdown = convert_to_markdown(article)
        
        # 保存文件
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        md_filename = filename or f"{sanitize_filename(article.title)}.md"
        md_path = os.path.join(output_dir, md_filename)
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"[INFO] 完成! 保存到: {md_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 抓取失败: {e}")
        return False
    finally:
        await page.close()


async def crawl_list_page(
    url: str,
    output_dir: str,
    download_imgs: bool = False,
    images_dir: Optional[str] = None,
    limit: Optional[int] = None,
    delay: float = 2.0,
    max_delay: float = 5.0,
    state_file: Optional[str] = None,
    resume: bool = False,
) -> None:
    """
    抓取列表页
    
    Args:
        url: 列表页 URL
        output_dir: 输出目录
        download_imgs: 是否下载图片
        images_dir: 图片目录
        limit: 最大抓取数
        delay: 基础延迟
        max_delay: 最大延迟
        state_file: 状态文件
        resume: 是否续传
    """
    import time
    start_time = time.time()
    
    platform = detect_platform(url)
    print(f"[INFO] 检测到列表页 ({platform.value})")
    
    # 加载状态
    state = None
    if resume and state_file:
        state = load_state(state_file)
    
    completed_urls = set(state["completed"]) if state else set()
    failed_urls = set(state["failed"]) if state else set()
    
    # 创建浏览器
    browser_manager = BrowserManager()
    await browser_manager.create_context()
    
    try:
        page = await browser_manager.new_page()
        
        print(f"[INFO] 正在提取文章链接...")
        await page.goto(url, wait_until='networkidle')
        
        links = await extract_list_links(page, platform)
        
        if limit:
            links = links[:limit]
        
        total = len(links)
        print(f"[INFO] 发现 {total} 篇文章")
        
        # 过滤已完成的
        links = [link for link in links if link not in completed_urls]
        
        if not links:
            print("[INFO] 所有文章已抓取完成")
            return
        
        await page.close()
        
        # 抓取每篇文章
        success_count = len(completed_urls)
        fail_count = len(failed_urls)
        
        for i, link in enumerate(links, 1):
            print(f"\n抓取进度: [{i}/{total}] | 当前: {link}")
            print(f"[INFO] 延迟 {max(0.5, delay):.1f} 秒...")
            actual_delay = random_delay(max(0.5, delay), max_delay)
            
            success = await crawl_single_article(
                link,
                output_dir,
                download_imgs=download_imgs,
                images_dir=images_dir,
                browser_manager=browser_manager,
            )
            
            if success:
                success_count += 1
                completed_urls.add(link)
            else:
                fail_count += 1
                failed_urls.add(link)
            
            # 保存状态
            if state_file:
                save_state(state_file, {
                    "url": url,
                    "total": total,
                    "completed": list(completed_urls),
                    "failed": list(failed_urls),
                })
            
            elapsed = time.time() - start_time
            remaining = int((total - i) * delay)
            print(f"预计剩余: {remaining} 秒 | 成功: {success_count} | 失败: {fail_count}")
        
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        print(f"\n[INFO] 完成! 保存到: {output_dir}")
        print(f"[INFO] 总计: {total} 篇 | 成功: {success_count} | 失败: {fail_count} | 耗时: {minutes}分{seconds}秒")
        
    finally:
        await browser_manager.close()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="URL to Markdown 抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument("url", help="文章页或列表页 URL")
    parser.add_argument("--output", default="misc/", help="输出目录 (默认: misc/)")
    parser.add_argument("--filename", help="文件名（仅单篇有效）")
    parser.add_argument("--download-images", action="store_true", help="下载图片到本地")
    parser.add_argument("--images-dir", help="图片保存目录")
    parser.add_argument("--limit", type=int, help="列表页最大抓取数")
    parser.add_argument("--delay", type=float, default=2.0, help="基础延迟秒数 (默认: 2)")
    parser.add_argument("--max-delay", type=float, default=5.0, help="最大延迟秒数 (默认: 5)")
    parser.add_argument("--no-randomize", action="store_true", help="禁用随机延迟")
    parser.add_argument("--resume", action="store_true", help="断点续传")
    parser.add_argument("--state", default="url2md-state.json", help="状态文件路径")
    
    args = parser.parse_args()
    
    # 检测页面类型
    platform = detect_platform(args.url)
    
    if is_article_page(args.url, platform):
        await crawl_single_article(
            args.url,
            args.output,
            filename=args.filename,
            download_imgs=args.download_images,
            images_dir=args.images_dir,
        )
    elif is_list_page(args.url, platform):
        await crawl_list_page(
            args.url,
            args.output,
            download_imgs=args.download_images,
            images_dir=args.images_dir,
            limit=args.limit,
            delay=args.delay,
            max_delay=args.max_delay,
            state_file=args.state if args.resume else None,
            resume=args.resume,
        )
    else:
        # 尝试作为文章页处理
        print("[WARN] 无法识别页面类型，尝试作为文章页处理")
        await crawl_single_article(
            args.url,
            args.output,
            filename=args.filename,
            download_imgs=args.download_images,
            images_dir=args.images_dir,
        )


if __name__ == "__main__":
    asyncio.run(main())