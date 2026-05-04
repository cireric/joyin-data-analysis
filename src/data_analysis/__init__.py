"""
Data Analysis Library

Core modules for generating styled Excel reports with period-over-period comparisons.
"""

from .loader import load_data, validate_data
from .analyzer import merge_periods, fill_missing_values, calculate_analysis, add_totals, calc_comparison, merge_maintenance_counts
from .report import generate_report, generate_group_summary, generate_supervisor_detail, reorder_value_columns, filter_group_metrics
from .styler import style_workbook, style_group_sheet, sanitize_filename
from .matcher import extract_machine_code, match_by_machine_code, get_matched_codes, get_unmatched_records
from .maintenance import load_maintenance_data, count_maintenance_by_point, generate_unmatched_sheet, process_maintenance_data

__all__ = [
    'load_data',
    'validate_data',
    'merge_periods',
    'fill_missing_values',
    'calculate_analysis',
    'add_totals',
    'calc_comparison',
    'merge_maintenance_counts',
    'generate_report',
    'generate_group_summary',
    'generate_supervisor_detail',
    'reorder_value_columns',
    'filter_group_metrics',
    'style_workbook',
    'style_group_sheet',
    'sanitize_filename',
    'extract_machine_code',
    'match_by_machine_code',
    'get_matched_codes',
    'get_unmatched_records',
    'load_maintenance_data',
    'count_maintenance_by_point',
    'generate_unmatched_sheet',
    'process_maintenance_data',
]