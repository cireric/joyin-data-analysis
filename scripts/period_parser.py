#!/usr/bin/env python3
"""
周期类型识别器

支持的格式:
- 年度: 2026
- 季度: 2026Q1
- 月度: 2026.03
- 自定义: 2026.04.13~2026.04.19
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PeriodType(Enum):
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    CUSTOM = "custom"


@dataclass
class PeriodInfo:
    period_type: PeriodType
    raw_input: str
    file_name: str
    label: str
    short_label: Optional[str] = None


class PeriodParser:
    """周期类型识别器"""
    
    FILE_PREFIX = "销售汇总表-"
    
    @classmethod
    def parse(cls, period_str: str, force_type: Optional[str] = None) -> PeriodInfo:
        """
        解析周期字符串
        
        Args:
            period_str: 周期字符串 (如: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19)
            force_type: 强制指定类型 (year/quarter/month/custom)
        
        Returns:
            PeriodInfo 对象
        
        Raises:
            ValueError: 无法识别格式时抛出
        """
        if force_type:
            return cls._parse_by_type(period_str, force_type)
        return cls._auto_detect(period_str)
    
    @classmethod
    def _parse_by_type(cls, period_str: str, force_type: str) -> PeriodInfo:
        """按指定类型解析"""
        type_map = {
            "year": PeriodType.YEAR,
            "quarter": PeriodType.QUARTER,
            "month": PeriodType.MONTH,
            "custom": PeriodType.CUSTOM,
        }
        
        if force_type not in type_map:
            raise ValueError(f"不支持的类型: {force_type}。支持的类型: year, quarter, month, custom")
        
        period_type = type_map[force_type]
        return cls._build_period_info(period_str, period_type)
    
    @classmethod
    def _auto_detect(cls, period_str: str) -> PeriodInfo:
        """自动识别周期类型"""
        if "~" in period_str:
            return cls._build_period_info(period_str, PeriodType.CUSTOM)
        
        if re.match(r"^\d{4}Q[1-4]$", period_str):
            return cls._build_period_info(period_str, PeriodType.QUARTER)
        
        if re.match(r"^\d{4}\.\d{2}$", period_str):
            return cls._build_period_info(period_str, PeriodType.MONTH)
        
        if re.match(r"^\d{4}$", period_str):
            return cls._build_period_info(period_str, PeriodType.YEAR)
        
        raise ValueError(
            f"无法识别周期格式 '{period_str}'。"
            f"支持的格式: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19"
        )
    
    @classmethod
    def _build_period_info(cls, period_str: str, period_type: PeriodType) -> PeriodInfo:
        """构建 PeriodInfo 对象"""
        file_name = f"{cls.FILE_PREFIX}{period_str}.xlsx"
        short_label = None
        
        if period_type == PeriodType.CUSTOM:
            short_label = cls._extract_short_label(period_str)
        
        return PeriodInfo(
            period_type=period_type,
            raw_input=period_str,
            file_name=file_name,
            label=period_str,
            short_label=short_label
        )
    
    @classmethod
    def _extract_short_label(cls, period_str: str) -> str:
        """
        从自定义范围提取简短标签
        
        输入: 2026.04.13~2026.04.19
        输出: 04.13~04.19
        """
        match = re.match(r"^\d{4}\.(\d{2}\.\d{2})~\d{4}\.(\d{2}\.\d{2})$", period_str)
        if match:
            return f"{match.group(1)}~{match.group(2)}"
        return period_str
    
    @classmethod
    def generate_title(cls, current: PeriodInfo, previous: PeriodInfo) -> str:
        """
        生成报表标题
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            报表标题字符串
        """
        type_labels = {
            PeriodType.YEAR: "年度",
            PeriodType.QUARTER: "季度",
            PeriodType.MONTH: "月度",
        }
        
        if current.period_type == PeriodType.CUSTOM:
            curr_short = current.short_label or current.label
            prev_short = previous.short_label or previous.label
            return f"{prev_short}与{curr_short}销售分析"
        
        type_label = type_labels.get(current.period_type, "")
        return f"{previous.label}-{current.label}{type_label}销售分析"
