#!/usr/bin/env python3
"""
单元测试 - 数据分析计算函数
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from data_analysis.analyzer import (
    calc_comparison,
    calc_comparison_vectorized,
    merge_periods,
    fill_missing_values,
    calculate_analysis,
    add_totals,
)


class TestCalcComparison:
    """calc_comparison 标量版本测试"""
    
    def test_normal_calculation(self):
        result = calc_comparison(120, 100)
        assert result == 0.2
    
    def test_negative_change(self):
        result = calc_comparison(80, 100)
        assert result == -0.2
    
    def test_current_nan(self):
        result = calc_comparison(np.nan, 100)
        assert result is None
    
    def test_previous_nan(self):
        result = calc_comparison(100, np.nan)
        assert result is None
    
    def test_both_nan(self):
        result = calc_comparison(np.nan, np.nan)
        assert result is None
    
    def test_previous_zero(self):
        result = calc_comparison(100, 0)
        assert result is None
    
    def test_both_zero(self):
        result = calc_comparison(0, 0)
        assert result is None
    
    def test_current_zero_previous_positive(self):
        result = calc_comparison(0, 100)
        assert result == -1.0
    
    def test_large_numbers(self):
        result = calc_comparison(1000000, 500000)
        assert result == 1.0
    
    def test_decimal_numbers(self):
        result = calc_comparison(1.5, 1.0)
        assert result == 0.5


class TestCalcComparisonVectorized:
    """calc_comparison_vectorized 向量化版本测试"""
    
    def test_normal_calculation(self):
        current = pd.Series([120, 80, 150])
        previous = pd.Series([100, 100, 100])
        result = calc_comparison_vectorized(current, previous)
        assert list(result) == [0.2, -0.2, 0.5]
    
    def test_with_nan_values(self):
        current = pd.Series([120, np.nan, 150])
        previous = pd.Series([100, 100, np.nan])
        result = calc_comparison_vectorized(current, previous)
        assert result[0] == 0.2
        assert pd.isna(result[1])
        assert pd.isna(result[2])
    
    def test_with_zero_previous(self):
        current = pd.Series([100, 0, 50])
        previous = pd.Series([0, 0, 100])
        result = calc_comparison_vectorized(current, previous)
        assert pd.isna(result[0])
        assert pd.isna(result[1])
        assert result[2] == -0.5
    
    def test_empty_series(self):
        current = pd.Series([], dtype=float)
        previous = pd.Series([], dtype=float)
        result = calc_comparison_vectorized(current, previous)
        assert len(result) == 0


class TestMergePeriods:
    """merge_periods 测试"""
    
    def test_basic_merge(self):
        data = {
            'current': pd.DataFrame({'点位名称': ['A', 'B'], '总杯数': [100, 200]}),
            'previous': pd.DataFrame({'点位名称': ['A', 'B'], '总杯数': [80, 180]})
        }
        periods = {'current': 'current', 'previous': 'previous'}
        value_columns = [{'name': '总杯数'}]
        
        result = merge_periods(data, periods, '点位名称', value_columns)
        
        assert '点位名称' in result.columns
        assert '总杯数_current' in result.columns
        assert '总杯数_previous' in result.columns
        assert len(result) == 2
    
    def test_outer_join(self):
        data = {
            'current': pd.DataFrame({'点位名称': ['A', 'B'], '总杯数': [100, 200]}),
            'previous': pd.DataFrame({'点位名称': ['B', 'C'], '总杯数': [180, 300]})
        }
        periods = {'current': 'current', 'previous': 'previous'}
        value_columns = [{'name': '总杯数'}]
        
        result = merge_periods(data, periods, '点位名称', value_columns)
        
        assert len(result) == 3
        assert 'A' in result['点位名称'].values
        assert 'C' in result['点位名称'].values


class TestFillMissingValues:
    """fill_missing_values 测试"""
    
    def test_fill_partial_missing(self):
        df = pd.DataFrame({
            '点位名称': ['A', 'B'],
            '总杯数_current': [100, np.nan],
            '总杯数_previous': [80, 180]
        })
        value_columns = [{'name': '总杯数'}]
        
        result = fill_missing_values(df, '点位名称', value_columns)
        
        assert result.loc[0, '总杯数_current'] == 100
        assert result.loc[0, '总杯数_previous'] == 80
    
    def test_fill_missing_in_one_period(self):
        df = pd.DataFrame({
            '点位名称': ['A', 'B'],
            '总杯数_current': [100, np.nan],
            '总杯数_previous': [np.nan, 180]
        })
        value_columns = [{'name': '总杯数'}]
        
        result = fill_missing_values(df, '点位名称', value_columns)
        
        assert result.loc[0, '总杯数_current'] == 100
        assert result.loc[0, '总杯数_previous'] == 0
        assert result.loc[1, '总杯数_current'] == 0
        assert result.loc[1, '总杯数_previous'] == 180


class TestCalculateAnalysis:
    """calculate_analysis 测试"""
    
    def test_yoy_calculation(self):
        df = pd.DataFrame({
            '点位名称': ['A', 'B'],
            '总杯数_current': [120, 80],
            '总杯数_previous': [100, 100]
        })
        value_columns = [{'name': '总杯数'}]
        
        result = calculate_analysis(df, value_columns, ['yoy'])
        
        assert '总杯数_yoy' in result.columns
        assert result.loc[0, '总杯数_yoy'] == 0.2
        assert result.loc[1, '总杯数_yoy'] == -0.2
    
    def test_no_yoy_analysis(self):
        df = pd.DataFrame({
            '点位名称': ['A', 'B'],
            '总杯数_current': [120, 80],
            '总杯数_previous': [100, 100]
        })
        value_columns = [{'name': '总杯数'}]
        
        result = calculate_analysis(df, value_columns, [])
        
        assert '总杯数_yoy' not in result.columns


class TestAddTotals:
    """add_totals 测试"""
    
    def test_totals_row(self):
        df = pd.DataFrame({
            '点位名称': ['A', 'B'],
            '总杯数_current': [100, 200],
            '总杯数_previous': [80, 180],
            '总杯数_yoy': [0.25, 0.111]
        })
        value_columns = [{'name': '总杯数'}]
        
        result = add_totals(df, '点位名称', value_columns, ['yoy'])
        
        assert len(result) == 3
        assert '总计' in result.iloc[-1]['点位名称']
        assert result.iloc[-1]['总杯数_current'] == 300
        assert result.iloc[-1]['总杯数_previous'] == 260


if __name__ == '__main__':
    pytest.main([__file__, '-v'])