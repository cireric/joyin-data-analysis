#!/usr/bin/env python3
"""
Markdown转PDF工具

用法:
    python scripts/md2pdf.py input.md
    python scripts/md2pdf.py input.md -o output.pdf
    python scripts/md2pdf.py input.md --pdf-engine xelatex
    python scripts/md2pdf.py input.md --toc --force
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from lib.converter_base import (
    PDF_ENGINE_PRIORITY,
    detect_chinese,
    find_pandoc,
    get_available_pdf_engines,
    get_chinese_font,
    parse_frontmatter,
    resolve_output,
    validate_input,
)


class Md2PdfError(Exception):
    """Markdown转PDF工具基础异常"""
    pass


class InputFileNotFoundError(Md2PdfError):
    """文件不存在异常"""
    pass


class InvalidMarkdownError(Md2PdfError):
    """无效Markdown文件异常"""
    pass


class ConversionError(Md2PdfError):
    """转换失败异常"""
    pass


class DependencyError(Md2PdfError):
    """依赖缺失异常"""
    pass


class EngineNotFoundError(Md2PdfError):
    """PDF引擎未找到异常"""
    pass


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Markdown转PDF工具 - 将Markdown文件转换为PDF文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s document.md
  %(prog)s document.md -o result.pdf
  %(prog)s document.md --pdf-engine xelatex
  %(prog)s document.md --toc
  %(prog)s document.md -o result.pdf --force
        """,
    )

    parser.add_argument("--version", action="version", version="md2pdf 1.0")
    parser.add_argument("input", help="输入Markdown文件路径")
    parser.add_argument(
        "-o", "--output", help="输出PDF文件路径 (默认: 输入文件名.pdf)"
    )
    parser.add_argument(
        "--pdf-engine",
        help="PDF引擎 (weasyprint/xelatex/wkhtmltopdf/pdflatex)",
    )
    parser.add_argument("--toc", action="store_true", help="生成目录")
    parser.add_argument("--debug", action="store_true", help="输出调试信息")
    parser.add_argument(
        "-f", "--force", action="store_true", help="强制覆盖已存在的输出文件"
    )

    return parser.parse_args(args)


def generate_install_guide() -> str:
    return """错误: 未找到可用的 PDF 引擎

请安装以下任一引擎：

1. WeasyPrint (推荐，纯 Python):
   - 运行: pip install weasyprint

2. XeLaTeX (推荐中文文档):
   - Windows: 下载 MiKTeX https://miktex.org/download
   - 或运行: winget install MiKTeX.MiKTeX

3. wkhtmltopdf:
   - Windows: https://wkhtmltopdf.org/downloads.html
   - 或运行: winget install wkhtmltopdf

4. pdfLaTeX:
   - Windows: 下载 MiKTeX https://miktex.org/download
"""


def select_pdf_engine(
    content: str, user_engine: Optional[str] = None, debug: bool = False
) -> str:
    if user_engine:
        if debug:
            print(f"使用用户指定的PDF引擎: {user_engine}")
        return user_engine

    available_engines = get_available_pdf_engines()

    if not available_engines:
        raise EngineNotFoundError(generate_install_guide())

    if detect_chinese(content):
        for engine in ["xelatex", "weasyprint"]:
            if engine in available_engines:
                if debug:
                    print(f"检测到中文内容，使用引擎: {engine}")
                return engine

    selected = available_engines[0]
    if debug:
        print(f"自动选择PDF引擎: {selected}")
    return selected


def convert_md_to_pdf(
    input_path: Path,
    output_path: Path,
    pdf_engine: Optional[str] = None,
    toc: bool = False,
    debug: bool = False,
) -> bool:
    try:
        import pypandoc
    except ImportError:
        raise DependencyError("pypandoc 未安装，请运行: pip install pypandoc")

    pandoc_path = find_pandoc()
    if pandoc_path:
        os.environ["PATH"] = (
            os.path.dirname(pandoc_path) + os.pathsep + os.environ.get("PATH", "")
        )
        if debug:
            print(f"找到 pandoc: {pandoc_path}")

    content = input_path.read_text(encoding="utf-8")
    processed_content = re.sub(r'!\[[^\]]*\]', '![]', content)
    
    lines = processed_content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('**作者：**'):
            author = line.replace('**作者：**', '').strip()
            new_lines.append(f"**作者：** {author}  ")
            i += 1
        elif line.startswith('**发布时间：**'):
            time = line.replace('**发布时间：**', '').strip()
            new_lines.append(f"**发布时间：** {time}  ")
            i += 1
        elif line.startswith('**来源：**'):
            url = line.replace('**来源：**', '').strip()
            new_lines.append(f"**来源：** [{url}]({url})")
            i += 1
        else:
            new_lines.append(lines[i])
            i += 1
    
    processed_content = '\n'.join(new_lines)
    
    selected_engine = select_pdf_engine(processed_content, pdf_engine, debug)
    frontmatter = parse_frontmatter(content)

    extra_args = ["--pdf-engine", selected_engine]

    css_file = None
    if selected_engine == "wkhtmltopdf":
        css_content = """
@page { margin: 10mm 15mm; }
body { background-color: white; margin: 0; padding: 0; }
h1 { margin-top: 0; margin-bottom: 0.3em; }
img { max-width: 480px; max-height: 600px; display: block; margin: 1em auto; object-fit: contain; }
figure { margin: 1em 0; text-align: center; }
p, h1, h2, h3, h4, h5, h6 { margin: 0.3em 0; }
a { color: #0066cc; text-decoration: none; }
"""
        css_file = output_path.with_suffix(".temp.css")
        css_file.write_text(css_content, encoding="utf-8")
        extra_args.extend(["--css", str(css_file)])

    if detect_chinese(processed_content):
        font = get_chinese_font()
        if font:
            extra_args.extend(["--variable", f"mainfont:{font}"])
            if debug:
                print(f"使用中文字体: {font}")

    if toc:
        extra_args.append("--toc")

    if "title" in frontmatter:
        extra_args.extend(["--metadata", f"title={frontmatter['title']}"])
    if "author" in frontmatter:
        extra_args.extend(["--metadata", f"author={frontmatter['author']}"])

    if debug:
        print(f"转换参数: input={input_path}, output={output_path}")
        print(f"  extra_args={extra_args}")

    temp_md = output_path.with_suffix(".temp.md")
    
    try:
        temp_md.write_text(processed_content, encoding="utf-8")
        pypandoc.convert_file(
            str(temp_md), "pdf", outputfile=str(output_path), extra_args=extra_args
        )
        return True
    except Exception as e:
        raise ConversionError(f"转换失败: {e}")
    finally:
        if temp_md.exists():
            temp_md.unlink()
        if css_file and css_file.exists():
            css_file.unlink()


def main():
    args = parse_args()

    try:
        input_path = validate_input(args.input, (".md", ".markdown"))
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        output_path = resolve_output(input_path, args.output, args.force, ".pdf")
    except FileExistsError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"正在转换: {input_path} -> {output_path}")

    try:
        convert_md_to_pdf(
            input_path, output_path, args.pdf_engine, args.toc, args.debug
        )
        print(f"转换完成: {output_path}")
    except Md2PdfError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
