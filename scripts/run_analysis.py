#!/usr/bin/env python3
"""
独立数据分析脚本 - 支持多种周期类型

用法:
    python scripts/run_analysis.py --current 2026 --previous 2025
    python scripts/run_analysis.py -c 2026Q1 -p 2025Q1
    python scripts/run_analysis.py -c 2026.03 -p 2026.02
    python scripts/run_analysis.py -c 2026.04.13~2026.04.19 -p 2026.04.06~2026.04.12
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from period_parser import PeriodParser, PeriodInfo
from file_validator import FileValidator

sys.path.insert(0, str(Path(__file__).parent.parent / '.opencode' / 'skills' / 'data-analysis-report' / 'scripts'))

from generate_report import (
    load_data, validate_data, merge_periods, fill_missing_values,
    calculate_analysis, add_totals, reorder_value_columns,
    generate_group_summary, filter_group_metrics,
    style_workbook, style_group_sheet, sanitize_filename
)
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

DEFAULT_VALUE_COLUMNS = [
    '总杯数', '总金额', '线上杯数', '线下杯数', '线上金额', '线下金额', '测试杯'
]

DEFAULT_GROUP_COLUMN = '督导人员'


def create_config(args, current_info: PeriodInfo, previous_info: PeriodInfo):
    """根据命令行参数创建配置"""
    current_path, previous_path = FileValidator.get_file_paths(current_info, previous_info)
    
    config = {
        'data_source': {
            'type': 'multi_file',
            'files': [
                str(current_path),
                str(previous_path)
            ]
        },
        'key_column': '点位名称',
        'value_columns': [{'name': col} for col in args.columns],
        'periods': {
            'current': current_info.label,
            'previous': previous_info.label,
            'current_file': current_info.file_name.replace('.xlsx', ''),
            'previous_file': previous_info.file_name.replace('.xlsx', '')
        },
        'analysis': ['yoy'],
        'output': {
            'dir': './output',
            'title': args.title or PeriodParser.generate_title(current_info, previous_info)
        }
    }
    
    if args.group:
        config['group_by'] = {
            'column': args.group,
            'sheet_name': f'{args.group}汇总',
            'metrics': 'auto',
            'null_handling': 'ignore'
        }
    
    return config


def generate_report_from_config(config):
    """根据配置生成报表"""
    data = load_data(config)
    validate_data(data, config['periods'], config['key_column'], config['value_columns'])
    
    merged = merge_periods(
        data, config['periods'], config['key_column'], config['value_columns']
    )
    merged = fill_missing_values(merged, config['key_column'], config['value_columns'])
    
    result = calculate_analysis(
        merged, config['value_columns'], config['analysis']
    )
    result = add_totals(
        result, config['key_column'], config['value_columns'], config['analysis']
    )
    
    reordered_columns = reorder_value_columns(config['value_columns'])
    
    output_cols = [config['key_column']]
    for vc in reordered_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        output_cols.extend([
            f"{col_name}_previous", f"{col_name}_current", f"{col_name}_yoy"
        ])
    
    result = result[output_cols]
    
    rename_map = {config['key_column']: config['key_column']}
    for vc in config['value_columns']:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        prev_label = config['periods']['previous']
        curr_label = config['periods']['current']
        rename_map[f"{col_name}_previous"] = f"{prev_label}{col_name}"
        rename_map[f"{col_name}_current"] = f"{curr_label}{col_name}"
        rename_map[f"{col_name}_yoy"] = f"{col_name}同比"
    
    result.rename(columns=rename_map, inplace=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = config['output']['title']
    
    for r in dataframe_to_rows(result, index=False, header=True):
        ws.append(r)
    
    style_workbook(ws, reordered_columns, config['analysis'])
    
    group_result = None
    if 'group_by' in config and config['group_by']:
        group_config = config['group_by']
        group_col = group_config['column']
        sheet_name = group_config.get('sheet_name', f"{group_col}汇总")
        metrics = filter_group_metrics(config['value_columns'], group_config.get('metrics', 'auto'))
        
        group_result = generate_group_summary(
            data, config['periods'], group_config,
            config['value_columns'], config['analysis']
        )
        
        ws2 = wb.create_sheet(sheet_name)
        for r in dataframe_to_rows(group_result, index=False, header=True):
            ws2.append(r)
        
        style_group_sheet(ws2, metrics)
    
    date_dir = datetime.now().strftime('%Y%m%d')
    output_dir = Path(config['output']['dir']) / date_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    time_str = datetime.now().strftime('%H%M%S')
    safe_title = sanitize_filename(config['output']['title'])
    output_file = output_dir / f"{safe_title}_{time_str}.xlsx"
    wb.save(output_file)
    
    return str(output_file), len(result) - 1, len(group_result) - 1 if group_result is not None else 0


def main():
    parser = argparse.ArgumentParser(
        description='生成销售数据分析报表 (支持年度/季度/月度/自定义时间范围)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 年度分析
  %(prog)s -c 2026 -p 2025
  
  # 季度分析
  %(prog)s -c 2026Q1 -p 2025Q1
  
  # 月度分析
  %(prog)s -c 2026.03 -p 2026.02
  
  # 自定义时间范围
  %(prog)s -c 2026.04.13~2026.04.19 -p 2026.04.06~2026.04.12
  
  # 强制指定类型
  %(prog)s -c 2026.03 -p 2026.02 --type quarter
  
  # 其他参数
  %(prog)s -c 2026.03 -p 2026.02 --group 督导人员
  %(prog)s -c 2026.03 -p 2026.02 --columns 总杯数 总金额
        '''
    )
    
    parser.add_argument('-c', '--current', required=True,
                        help='当前期 (如: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19)')
    parser.add_argument('-p', '--previous', required=True,
                        help='对比期 (如: 2025, 2025Q1, 2026.02, 2026.04.06~2026.04.12)')
    parser.add_argument('--type', dest='period_type', choices=['year', 'quarter', 'month', 'custom'],
                        help='强制指定周期类型 (默认自动识别)')
    parser.add_argument('-g', '--group', default=DEFAULT_GROUP_COLUMN,
                        help=f'分组列 (默认: {DEFAULT_GROUP_COLUMN})')
    parser.add_argument('--columns', nargs='+', default=DEFAULT_VALUE_COLUMNS,
                        help=f'分析列 (默认: {DEFAULT_VALUE_COLUMNS})')
    parser.add_argument('-t', '--title', help='报表标题')
    
    args = parser.parse_args()
    
    try:
        current_info = PeriodParser.parse(args.current, args.period_type)
        previous_info = PeriodParser.parse(args.previous, args.period_type)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    
    valid, errors = FileValidator.validate(current_info, previous_info)
    if not valid:
        for error in errors:
            print(error)
        sys.exit(1)
    
    print(f"数据源: {current_info.file_name}, {previous_info.file_name}")
    
    config = create_config(args, current_info, previous_info)
    
    print(f"正在生成报表: {previous_info.label} vs {current_info.label}")
    
    output_file, point_count, group_count = generate_report_from_config(config)
    
    print(f"报表已生成: {output_file}")
    print(f"点位数量: {point_count}")
    if group_count > 0:
        print(f"分组汇总: {group_count} 条")


if __name__ == '__main__':
    main()
