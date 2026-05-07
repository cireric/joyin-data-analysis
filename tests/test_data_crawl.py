# tests/test_data_crawl.py
"""data_crawl 模块测试"""

import json
import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.data_crawl.utils import (
    random_delay,
    sanitize_filename,
    load_state,
    save_state,
)


class TestRandomDelay:
    def test_random_delay_returns_float(self):
        with patch('src.data_crawl.utils.time.sleep'):
            result = random_delay(2, 5)
            assert isinstance(result, float)

    def test_random_delay_within_range(self):
        with patch('src.data_crawl.utils.time.sleep'):
            for _ in range(100):
                result = random_delay(2, 5)
                assert 2 <= result <= 6  # delay + random(0, 1)

    def test_random_delay_default_values(self):
        with patch('src.data_crawl.utils.time.sleep'):
            result = random_delay()
            assert 2 <= result <= 6


class TestSanitizeFilename:
    def test_removes_invalid_characters(self):
        assert sanitize_filename("hello<>:\"/\\|?*world") == "helloworld"

    def test_replaces_spaces_with_underscores(self):
        assert sanitize_filename("hello world") == "hello_world"

    def test_truncates_long_filename(self):
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_removes_leading_trailing_spaces(self):
        assert sanitize_filename("  hello  ") == "hello"

    def test_empty_string_returns_untitled(self):
        assert sanitize_filename("") == "untitled"


class TestStateManagement:
    def test_save_and_load_state(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            state_file = f.name
        
        try:
            state = {
                "url": "https://example.com",
                "total": 10,
                "completed": ["url1", "url2"],
                "failed": ["url3"],
            }
            save_state(state_file, state)
            loaded = load_state(state_file)
            
            assert loaded["url"] == state["url"]
            assert loaded["total"] == state["total"]
            assert loaded["completed"] == state["completed"]
            assert loaded["failed"] == state["failed"]
        finally:
            if os.path.exists(state_file):
                os.remove(state_file)

    def test_load_state_file_not_exists(self):
        result = load_state("/nonexistent/path/state.json")
        assert result is None


from src.data_crawl.browser import create_browser_context, BrowserManager


class TestBrowserManager:
    @pytest.mark.asyncio
    async def test_create_browser_context(self):
        with patch('src.data_crawl.browser.async_playwright') as mock_pw:
            mock_playwright = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            
            mock_pw_instance = AsyncMock()
            mock_pw_instance.start = AsyncMock(return_value=mock_playwright)
            mock_pw.return_value = mock_pw_instance
            
            mock_playwright.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            
            manager = BrowserManager()
            context = await manager.create_context()
            
            assert context is not None
            mock_browser.new_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_context_has_user_agent(self):
        with patch('src.data_crawl.browser.async_playwright') as mock_pw:
            mock_playwright = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            
            mock_pw_instance = AsyncMock()
            mock_pw_instance.start = AsyncMock(return_value=mock_playwright)
            mock_pw.return_value = mock_pw_instance
            
            mock_playwright.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            
            manager = BrowserManager()
            await manager.create_context()
            
            call_kwargs = mock_browser.new_context.call_args[1]
            assert 'user_agent' in call_kwargs
            assert 'Mozilla' in call_kwargs['user_agent']
