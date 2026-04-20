#!/usr/bin/env python3
"""
PDF转Word工具

用法:
    python scripts/pdf2word.py input.pdf
    python scripts/pdf2word.py input.pdf -o output.docx
    python scripts/pdf2word.py input.pdf --pages 1-5
"""

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='PDF转Word工具 - 将PDF文件转换为可编辑的Word文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s document.pdf
  %(prog)s document.pdf -o result.docx
  %(prog)s document.pdf --pages 1-5
  %(prog)s document.pdf --pages 1,3,5-10
        '''
    )
    
    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('-o', '--output', help='输出Word文件路径 (默认: 输入文件名.docx)')
    parser.add_argument('--pages', help='页码范围 (如: 1-5, 1,3,5-10)')
    
    return parser.parse_args()


def main():
    args = parse_args()
    print(f"输入文件: {args.input}")
    print(f"输出文件: {args.output}")
    print(f"页码范围: {args.pages}")


if __name__ == '__main__':
    main()
