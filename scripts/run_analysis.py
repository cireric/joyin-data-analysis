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

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

from data_analysis import generate_report
from period_parser import PeriodParser, PeriodInfo
from file_validator import FileValidator

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
    parser.add_argument('-m', '--maintenance', help='兼职运维表路径 (可选)')
    
    args = parser.parse_args()
    
    try:
        current_info = PeriodParser.parse(args.current, args.period_type)
        previous_info = PeriodParser.parse(args.previous, args.period_type)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    
    try:
        FileValidator.validate(current_info, previous_info)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    print(f"数据源: {current_info.file_name}, {previous_info.file_name}")
    
    config = create_config(args, current_info, previous_info)
    
    print(f"正在生成报表: {previous_info.label} vs {current_info.label}")
    
    if args.maintenance:
        print(f"运维数据: {args.maintenance}")
    
    output_file, point_count, group_count, supervisor_count, unmatched_count = generate_report(
        config, maintenance_file=args.maintenance
    )
    
    print(f"报表已生成: {output_file}")
    print(f"点位数量: {point_count}")
    if group_count > 0:
        print(f"分组汇总: {group_count} 条")
    if supervisor_count > 0:
        print(f"督导详细页: {supervisor_count} 个")
    if unmatched_count > 0:
        print(f"待确认运维: {unmatched_count} 条")


if __name__ == '__main__':
    main()