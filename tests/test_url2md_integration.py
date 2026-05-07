# tests/test_url2md_integration.py
"""url2md 集成测试"""

import os
import tempfile
import pytest
from pathlib import Path


class TestURL2MDIntegration:
    """集成测试 - 需要网络连接"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_crawl_wechat_article(self):
        """测试微信公众号文章抓取"""
        import asyncio
        from scripts.url2md import crawl_single_article
        
        with tempfile.TemporaryDirectory() as tmpdir:
            url = "https://mp.weixin.qq.com/s/o6r4R00qjBS_gSu2C8RyyQ"
            
            success = await crawl_single_article(url, tmpdir)
            
            assert success == True
            
            # 检查文件是否存在
            md_files = list(Path(tmpdir).glob("*.md"))
            assert len(md_files) >= 1
            
            # 检查文件内容
            content = md_files[0].read_text(encoding='utf-8')
            assert "# " in content
            assert "沙丘" in content
