"""
Data Analysis Library

Core modules for generating styled Excel reports with period-over-period comparisons.
"""

from .loader import load_data, validate_data
from .analyzer import merge_periods, fill_missing_values, calculate_analysis, add_totals, calc_comparison
from .report import generate_report, generate_group_summary, generate_supervisor_detail, reorder_value_columns, filter_group_metrics
from .styler import style_workbook, style_group_sheet, sanitize_filename

__all__ = [
    'load_data',
    'validate_data',
    'merge_periods',
    'fill_missing_values',
    'calculate_analysis',
    'add_totals',
    'calc_comparison',
    'generate_report',
    'generate_group_summary',
    'generate_supervisor_detail',
    'reorder_value_columns',
    'filter_group_metrics',
    'style_workbook',
    'style_group_sheet',
    'sanitize_filename',
]