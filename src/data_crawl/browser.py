# src/data_crawl/browser.py
"""浏览器配置与风控规避"""

import asyncio
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None
    Page = None


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, headless: bool = True):
        """
        初始化浏览器管理器
        
        Args:
            headless: 是否无头模式
        """
        if async_playwright is None:
            raise ImportError("playwright not installed. Run: pip install playwright")
        
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def create_context(
        self,
        cookies_file: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> BrowserContext:
        """
        创建浏览器上下文
        
        Args:
            cookies_file: cookies 文件路径
            user_agent: 自定义 User-Agent
        
        Returns:
            浏览器上下文
        """
        if self._playwright is None:
            self._playwright = await async_playwright().start()

        if self._browser is None:
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

        self._context = await self._browser.new_context(
            user_agent=user_agent or DEFAULT_USER_AGENT,
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        # 加载 cookies
        if cookies_file and Path(cookies_file).exists():
            import json
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                await self._context.add_cookies(cookies)

        return self._context

    async def save_cookies(self, cookies_file: str) -> None:
        """
        保存 cookies 到文件
        
        Args:
            cookies_file: cookies 文件路径
        """
        if self._context is None:
            return
        
        cookies = await self._context.cookies()
        
        path = Path(cookies_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

    async def new_page(self) -> Page:
        """
        创建新页面
        
        Returns:
            页面对象
        """
        if self._context is None:
            await self.create_context()
        return await self._context.new_page()

    async def close(self) -> None:
        """关闭浏览器"""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None


async def create_browser_context(
    headless: bool = True,
    cookies_file: Optional[str] = None,
) -> BrowserManager:
    """
    创建浏览器管理器（便捷函数）
    
    Args:
        headless: 是否无头模式
        cookies_file: cookies 文件路径
    
    Returns:
        浏览器管理器
    """
    manager = BrowserManager(headless=headless)
    await manager.create_context(cookies_file=cookies_file)
    return manager
