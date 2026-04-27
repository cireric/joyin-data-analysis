# md2word 实现计划

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 `scripts/md2word.py` 将 Markdown 文件转换为 Word 文档

**Architecture:** 参照 `pdf2word.py` 模式，采用 pypandoc 调用 Pandoc 引擎，支持 --reference-docx 样式模板和 --toc 目录

**Tech Stack:** Python 3, pypandoc, Pandoc

---

### Task 1: 更新依赖和 Makefile

**Files:**
- Modify: `requirements.txt`
- Modify: `Makefile`

- [ ] **Step 1: requirements.txt 添加 pypandoc**

编辑 `requirements.txt` 在末尾添加一行：
```
pypandoc==1.14
```

- [ ] **Step 2: Makefile 添加 md2word 命令**

编辑 `Makefile`，在 `clean:` 之前添加：
```makefile
md2word:
	@.venv\Scripts\python.exe scripts/md2word.py $(filter-out $@,$(MAKECMDGOALS))
```

在 `help:` 中添加一行：
```makefile
	@echo   make md2word input.md [ARGS]                 # Markdown to Word
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt Makefile
git commit -m "chore: add pypandoc dependency and md2word make target"
```

### Task 2: 实现 md2word.py

**Files:**
- Create: `scripts/md2word.py`

- [ ] **Step 1: 创建脚本框架**

```python
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
import sys
from pathlib import Path


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
```

- [ ] **Step 2: 实现参数解析**

```python
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

    parser.add_argument('input', help='输入Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出Word文件路径 (默认: 输入文件名.docx)')
    parser.add_argument('--reference-docx', help='Pandoc样式参考模板 (用于自定义合同样式)')
    parser.add_argument('--toc', action='store_true', help='生成目录')
    parser.add_argument('--debug', action='store_true', help='输出调试信息')
    parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的输出文件')

    return parser.parse_args()
```

- [ ] **Step 3: 实现文件验证**

```python
def validate_input(input_path: str) -> Path:
    path = Path(input_path)

    if not path.exists():
        raise InputFileNotFoundError(f"文件不存在: {input_path}")

    if path.suffix.lower() not in ('.md', '.markdown'):
        raise InvalidMarkdownError(f"文件格式错误: 需要Markdown文件(.md)，当前为 {path.suffix}")

    return path
```

- [ ] **Step 4: 实现输出路径处理**

```python
def resolve_output(input_path: Path, output_arg: str, force: bool) -> Path:
    if output_arg:
        output_path = Path(output_arg)
    else:
        output_path = input_path.with_suffix('.docx')

    if output_path.exists() and not force:
        print(f"错误: 输出文件已存在: {output_path}", file=sys.stderr)
        print(f"提示: 使用 --force 参数强制覆盖", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path
```

- [ ] **Step 5: 实现核心转换逻辑**

```python
def convert_md_to_docx(input_path: Path, output_path: Path,
                       reference_docx: str = None, toc: bool = False,
                       debug: bool = False) -> bool:
    try:
        import pypandoc
    except ImportError:
        raise DependencyError(
            "pypandoc 未安装，请运行: pip install pypandoc"
        )

    try:
        extra_args = []
        if reference_docx:
            extra_args.extend(['--reference-docx', reference_docx])
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
    except Exception as e:
        raise ConversionError(f"转换失败: {e}")
```

- [ ] **Step 6: 实现 main 函数**

```python
def main():
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
```

- [ ] **Step 7: Commit**

```bash
git add scripts/md2word.py
git commit -m "feat: add md2word script for Markdown to Word conversion"
```

### Task 3: 验证安装和基本功能

- [ ] **Step 1: 安装依赖**

```bash
.venv\Scripts\pip install pypandoc
```

- [ ] **Step 2: 创建测试用 Markdown 文件并运行**

创建 test.md:
```markdown
# 测试合同

## 第一条 定义

本合同中使用的大写术语具有以下含义：

- **甲方**：采购方
- **乙方**：供应方

## 第二条 合同金额

| 项目 | 金额 |
|------|------|
| 服务费 | ¥10,000 |
| 税费 | ¥1,000 |
| **合计** | **¥11,000** |

## 第三条 生效

本合同自双方签字之日起生效。
```

运行：
```bash
.venv\Scripts\python scripts/md2word.py test.md -o output/test.docx --force
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/2026-04-26-md2word-plan.md
git commit -m "docs: add md2word implementation plan"
```
