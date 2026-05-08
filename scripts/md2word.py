#!/usr/bin/env python3
"""
Markdown转Word工具

用法:
    python scripts/md2word.py input.md
    python scripts/md2word.py input.md -o output.docx
    python scripts/md2word.py input.md --reference-docx template.docx
    python scripts/md2word.py input.md --toc --force
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from lib.converter_base import (
    validate_input as _validate_input,
    resolve_output as _resolve_output,
    find_pandoc,
)


class Md2WordError(Exception):
    """Markdown转Word工具基础异常"""
    pass


class InputFileNotFoundError(Md2WordError):
    pass


class InvalidMarkdownError(Md2WordError):
    pass


class ConversionError(Md2WordError):
    pass


class DependencyError(Md2WordError):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description='Markdown转Word工具 - 将Markdown文件转换为Word文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s document.md
  %(prog)s document.md -o result.docx
  %(prog)s document.md --reference-docx template.docx
  %(prog)s document.md --toc
  %(prog)s document.md -o result.docx --force
        '''
    )

    # 版本查询
    parser.add_argument('--version', action='version', version='md2word 1.0')

    parser.add_argument('input', help='输入Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出Word文件路径 (默认: 输入文件名.docx)')
    parser.add_argument('--reference-docx', help='Pandoc样式参考模板 (用于自定义合同样式)')
    parser.add_argument('--toc', action='store_true', help='生成目录')
    parser.add_argument('--debug', action='store_true', help='输出调试信息')
    parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的输出文件')

    return parser.parse_args()


def validate_input(input_path: str) -> Path:
    return _validate_input(input_path, (".md", ".markdown"))


def resolve_output(input_path: Path, output_arg: str, force: bool) -> Path:
    return _resolve_output(input_path, output_arg, force, ".docx")


def _default_font_template_path() -> Optional[str]:
    """Return the default Windows font template path if it exists.
    Path is relative to the data_analysis project structure:
    data_analysis/docs/superpowers/templates/windows-default-font-template.docx
    """
    base = Path(__file__).resolve().parents[1]  # .../data_analysis/scripts -> .../data_analysis
    candidate = base / "docs" / "superpowers" / "templates" / "windows-default-font-template.docx"
    if candidate.exists():
        return str(candidate)
    return None


def _choose_template(user_template: Optional[str]) -> Optional[str]:
    """Decide which template to use for Pandoc conversion.
    Priority: user-specified template > default Windows font template.
    """
    if user_template:
        p = Path(user_template)
        if p.exists():
            return str(p)
    # try default template if present
    default_t = _default_font_template_path()
    if default_t:
        return default_t
    return None


def convert_md_to_docx(input_path: Path, output_path: Path,
                       reference_docx: str = None, toc: bool = False,
                       debug: bool = False) -> bool:
    try:
        import pypandoc
    except ImportError:
        raise DependencyError(
            "pypandoc 未安装，请运行: pip install pypandoc"
        )

    pandoc_path = find_pandoc()
    if pandoc_path:
        os.environ['PATH'] = os.path.dirname(pandoc_path) + os.pathsep + os.environ.get('PATH', '')
        if debug:
            print(f"找到 pandoc: {pandoc_path}")

    try:
        # Decide which template to use (user-specified preferred, otherwise default Windows font template)
        template_path = _choose_template(reference_docx)
        extra_args = []
        if template_path:
            extra_args.extend(['--reference-docx', template_path])
        if toc:
            extra_args.append('--toc')

        if debug:
            print(f"转换参数: input={input_path}, output={output_path}")
            print(f"  extra_args={extra_args}")

        pypandoc.convert_file(
            str(input_path),
            'docx',
            outputfile=str(output_path),
            extra_args=extra_args
        )
        return True
    except (RuntimeError, OSError) as e:
        raise DependencyError(
            f"未找到 pandoc，请手动安装: https://pandoc.org/installing.html\n"
            f"或运行: pip install pypandoc_binary (会自动包含 pandoc)"
        )
    except Exception as e:
        raise ConversionError(f"转换失败: {e}")


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    args = parse_args()

    try:
        input_path = validate_input(args.input)
    except Md2WordError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = resolve_output(input_path, args.output, args.force)

    print(f"正在转换: {input_path} -> {output_path}")
    try:
        convert_md_to_docx(input_path, output_path, args.reference_docx, args.toc, args.debug)
        print(f"转换完成: {output_path}")
    except Md2WordError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
