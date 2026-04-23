#!/usr/bin/env python3
"""
文件验证器 - 检查数据文件是否存在
"""

from pathlib import Path

from period_parser import PeriodInfo


class FileValidator:
    """数据文件验证器"""
    
    DATA_DIR = Path(__file__).parent.parent / "data"
    
    @classmethod
    def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> None:
        """
        验证数据文件是否存在
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Raises:
            FileNotFoundError: 当数据文件不存在时抛出
        """
        current_path = cls.DATA_DIR / current.file_name
        previous_path = cls.DATA_DIR / previous.file_name
        
        if not current_path.exists():
            raise FileNotFoundError(f"未找到当前期数据文件: data/{current.file_name}")
        
        if not previous_path.exists():
            raise FileNotFoundError(f"未找到对比期数据文件: data/{previous.file_name}")
    
    @classmethod
    def get_file_paths(cls, current: PeriodInfo, previous: PeriodInfo) -> tuple:
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
