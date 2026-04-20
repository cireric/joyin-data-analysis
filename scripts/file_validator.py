#!/usr/bin/env python3
"""
文件验证器 - 检查数据文件是否存在
"""

from pathlib import Path
from typing import List, Tuple

from period_parser import PeriodInfo


class FileValidator:
    """数据文件验证器"""
    
    DATA_DIR = Path("data")
    
    @classmethod
    def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> Tuple[bool, List[str]]:
        """
        验证数据文件是否存在
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            (是否全部存在, 错误信息列表)
        """
        errors = []
        
        current_path = cls.DATA_DIR / current.file_name
        previous_path = cls.DATA_DIR / previous.file_name
        
        if not current_path.exists():
            errors.append(f"错误: 未找到当前期数据文件: data/{current.file_name}")
        
        if not previous_path.exists():
            errors.append(f"错误: 未找到对比期数据文件: data/{previous.file_name}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_file_paths(cls, current: PeriodInfo, previous: PeriodInfo) -> Tuple[Path, Path]:
        """
        获取数据文件完整路径
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            (当前期路径, 对比期路径)
        """
        return (
            cls.DATA_DIR / current.file_name,
            cls.DATA_DIR / previous.file_name
        )
