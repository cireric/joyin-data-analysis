#!/usr/bin/env python3
"""
单元测试 - 数据分析计算函数
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / '.opencode' / 'skills' / 'data-analysis-report' / 'scripts'))

import pytest
import pandas as pd
import numpy as np
from generate_report import calc_comparison


class TestCalcComparison:
    """calc_comparison 测试"""
    
    def test_normal_calculation(self):
        """测试正常计算"""
        result = calc_comparison(120, 100)
        assert result == 0.2
    
    def test_negative_change(self):
        """测试负增长"""
        result = calc_comparison(80, 100)
        assert result == -0.2
    
    def test_current_nan(self):
        """测试当前值为NaN"""
        result = calc_comparison(np.nan, 100)
        assert result == 'N/A'
    
    def test_previous_nan(self):
        """测试对比值为NaN"""
        result = calc_comparison(100, np.nan)
        assert result == 'N/A'
    
    def test_both_nan(self):
        """测试两者都为NaN"""
        result = calc_comparison(np.nan, np.nan)
        assert result == 'N/A'
    
    def test_previous_zero(self):
        """测试对比值为零"""
        result = calc_comparison(100, 0)
        assert result == 'N/A'
    
    def test_both_zero(self):
        """测试两者都为零"""
        result = calc_comparison(0, 0)
        assert result == 'N/A'
    
    def test_current_zero_previous_positive(self):
        """测试当前值为零，对比值正数"""
        result = calc_comparison(0, 100)
        assert result == -1.0
    
    def test_large_numbers(self):
        """测试大数计算"""
        result = calc_comparison(1000000, 500000)
        assert result == 1.0
    
    def test_decimal_numbers(self):
        """测试小数计算"""
        result = calc_comparison(1.5, 1.0)
        assert result == 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])