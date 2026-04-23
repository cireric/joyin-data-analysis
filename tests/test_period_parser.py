#!/usr/bin/env python3
"""
单元测试 - 周期解析器
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import pytest
from period_parser import PeriodParser, PeriodType, PeriodInfo


class TestPeriodParser:
    """PeriodParser 测试"""
    
    def test_parse_year(self):
        """测试年度格式"""
        info = PeriodParser.parse('2026')
        assert info.period_type == PeriodType.YEAR
        assert info.file_name == '销售汇总表-2026.xlsx'
        assert info.label == '2026'
    
    def test_parse_quarter(self):
        """测试季度格式"""
        info = PeriodParser.parse('2026Q1')
        assert info.period_type == PeriodType.QUARTER
        assert info.file_name == '销售汇总表-2026Q1.xlsx'
        assert info.label == '2026Q1'
    
    def test_parse_quarter_all(self):
        """测试所有季度"""
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            info = PeriodParser.parse(f'2026{q}')
            assert info.period_type == PeriodType.QUARTER
    
    def test_parse_month(self):
        """测试月度格式"""
        info = PeriodParser.parse('2026.03')
        assert info.period_type == PeriodType.MONTH
        assert info.file_name == '销售汇总表-2026.03.xlsx'
        assert info.label == '2026.03'
    
    def test_parse_custom(self):
        """测试自定义时间范围"""
        info = PeriodParser.parse('2026.04.13~2026.04.19')
        assert info.period_type == PeriodType.CUSTOM
        assert info.file_name == '销售汇总表-2026.04.13~2026.04.19.xlsx'
        assert info.short_label == '04.13~04.19'
    
    def test_force_type_year(self):
        """测试强制指定年度类型"""
        info = PeriodParser.parse('2026.03', force_type='year')
        assert info.period_type == PeriodType.YEAR
    
    def test_force_type_quarter(self):
        """测试强制指定季度类型"""
        info = PeriodParser.parse('2026.03', force_type='quarter')
        assert info.period_type == PeriodType.QUARTER
    
    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(ValueError):
            PeriodParser.parse('invalid')
    
    def test_invalid_quarter(self):
        """测试无效季度"""
        with pytest.raises(ValueError):
            PeriodParser.parse('2026Q5')
    
    def test_generate_title_year(self):
        """测试年度标题生成"""
        current = PeriodParser.parse('2026')
        previous = PeriodParser.parse('2025')
        title = PeriodParser.generate_title(current, previous)
        assert title == '2025-2026年度销售分析'
    
    def test_generate_title_month(self):
        """测试月度标题生成"""
        current = PeriodParser.parse('2026.03')
        previous = PeriodParser.parse('2026.02')
        title = PeriodParser.generate_title(current, previous)
        assert title == '2026.02-2026.03月度销售分析'
    
    def test_generate_title_custom(self):
        """测试自定义时间范围标题生成"""
        current = PeriodParser.parse('2026.04.13~2026.04.19')
        previous = PeriodParser.parse('2026.04.06~2026.04.12')
        title = PeriodParser.generate_title(current, previous)
        assert title == '04.06~04.12与04.13~04.19销售分析'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
