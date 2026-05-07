# src/data_crawl/utils.py
"""工具函数：延迟、重试、文件名清理、状态管理"""

import json
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


def random_delay(base_delay: float = 2.0, max_delay: float = 5.0) -> float:
    """
    生成随机延迟时间
    
    Args:
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
    
    Returns:
        实际延迟时间
    """
    jitter = random.uniform(0, 1)
    delay = min(base_delay + jitter, max_delay)
    time.sleep(delay)
    return delay


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        max_length: 最大长度
    
    Returns:
        清理后的文件名
    """
    if not filename or not filename.strip():
        return "untitled"
    
    # 移除首尾空格
    filename = filename.strip()
    
    # Windows 非法字符
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '', filename)
    
    # 替换空格为下划线
    filename = filename.replace(' ', '_')
    
    # 截断过长文件名
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename or "untitled"


def load_state(state_file: str) -> Optional[Dict[str, Any]]:
    """
    加载状态文件
    
    Args:
        state_file: 状态文件路径
    
    Returns:
        状态字典，文件不存在返回 None
    """
    path = Path(state_file)
    if not path.exists():
        return None
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_state(state_file: str, state: Dict[str, Any]) -> None:
    """
    保存状态文件
    
    Args:
        state_file: 状态文件路径
        state: 状态字典
    """
    path = Path(state_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    state["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def exponential_backoff(attempt: int, base: float = 1.0, max_wait: float = 60.0) -> float:
    """
    指数退避计算
    
    Args:
        attempt: 尝试次数
        base: 基础等待时间
        max_wait: 最大等待时间
    
    Returns:
        等待时间
    """
    wait = min(base * (2 ** attempt), max_wait)
    return wait
