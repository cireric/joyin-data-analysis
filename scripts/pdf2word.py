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


class PDF2WordError(Exception):
    """PDF转Word工具基础异常"""
    pass


class FileNotFoundError_(PDF2WordError):
    """文件不存在异常"""
    pass


class InvalidPDFError(PDF2WordError):
    """无效PDF文件异常"""
    pass


class InvalidPageRangeError(PDF2WordError):
    """无效页码范围异常"""
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
    parser.add_argument('--mode', choices=['normal', 'strict'], default='normal',
                        help='转换模式: normal(默认, 平衡速度与质量) / strict(严格模式, 更精确)')
    parser.add_argument('--debug', action='store_true',
                        help='输出调试信息')
    
    return parser.parse_args()


def validate_input(input_path: str) -> Path:
    """
    验证输入文件
    
    Args:
        input_path: 输入文件路径
        
    Returns:
        Path: 验证后的文件路径
        
    Raises:
        FileNotFoundError_: 文件不存在
        InvalidPDFError: 文件格式错误
    """
    path = Path(input_path)
    
    if not path.exists():
        raise FileNotFoundError_(f"文件不存在: {input_path}")
    
    if path.suffix.lower() != '.pdf':
        raise InvalidPDFError(f"文件格式错误: 需要PDF文件，当前为 {path.suffix}")
    
    return path


def parse_page_range(page_str: str) -> list:
    """
    解析页码范围字符串
    
    支持格式:
        1-5      -> [1, 2, 3, 4, 5]
        1,3,5    -> [1, 3, 5]
        1-3,5,7-9 -> [1, 2, 3, 5, 7, 8, 9]
    
    Args:
        page_str: 页码范围字符串
        
    Returns:
        排序后的页码列表，None表示全部页面
        
    Raises:
        InvalidPageRangeError: 页码范围无效
    """
    if not page_str:
        return None
    
    pages = set()
    parts = page_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                if start > end:
                    raise InvalidPageRangeError(f"页码范围无效: {page_str} (起始页 {start} 大于结束页 {end})")
                pages.update(range(start, end + 1))
            except ValueError:
                raise InvalidPageRangeError(f"页码范围无效: {page_str}")
        else:
            try:
                pages.add(int(part))
            except ValueError:
                raise InvalidPageRangeError(f"页码范围无效: {page_str}")
    
    return sorted(pages)


def convert_pdf_to_docx(input_path: Path, output_path: Path, pages: list = None,
                        mode: str = 'normal', debug: bool = False) -> bool:
    """
    将PDF转换为Word文档
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出Word文件路径
        pages: 页码列表，None表示全部页面
        mode: 转换模式，'normal'或'strict'
        debug: 是否输出调试信息
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from pdf2docx import Converter
        
        convert_params = {}
        
        if mode == 'strict':
            convert_params = {
                'multi_processing': False,
                'debug': debug,
            }
        else:
            convert_params = {
                'multi_processing': True,
                'debug': debug,
            }
        
        cv = Converter(str(input_path))
        try:
            if pages:
                cv.convert(str(output_path), pages=pages, **convert_params)
            else:
                cv.convert(str(output_path), **convert_params)
            return True
        finally:
            cv.close()
        
    except Exception as e:
        print(f"错误: 转换失败: {e}", file=sys.stderr)
        return False


def main():
    args = parse_args()
    
    try:
        input_path = validate_input(args.input)
        pages = parse_page_range(args.pages)
    except PDF2WordError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.docx')
    
    mode_str = "严格模式" if args.mode == 'strict' else "普通模式"
    print(f"正在转换: {input_path} -> {output_path} ({mode_str})")
    
    if convert_pdf_to_docx(input_path, output_path, pages, args.mode, args.debug):
        print(f"转换完成: {output_path}")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
