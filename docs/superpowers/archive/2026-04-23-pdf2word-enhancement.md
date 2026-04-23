# PDF转Word工具增强实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化 pdf2word.py 脚本，统一错误处理、添加输出目录自动创建、添加 --force 参数、添加 --preset 预设模式提升格式还原度。

**Architecture:** 在现有脚本基础上重构错误处理为异常风格，添加预设配置模块，增强命令行参数。

**Tech Stack:** Python 3, pdf2docx, argparse

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `scripts/pdf2word.py` | 修改 | 主要优化目标 |

---

### Task 1: 统一错误处理为异常风格

**Files:**
- Modify: `scripts/pdf2word.py`

**目标:** 将 `validate_input` 和 `parse_page_range` 函数从 `sys.exit()` 改为抛出异常，与 `convert_pdf_to_docx` 保持一致。

- [ ] **Step 1: 添加自定义异常类**

在文件顶部导入后添加：

```python
class PDF2WordError(Exception):
    """PDF转Word工具基础异常"""
    pass

class FileNotFoundError(PDF2WordError):
    """文件不存在异常"""
    pass

class InvalidPDFError(PDF2WordError):
    """无效PDF文件异常"""
    pass

class InvalidPageRangeError(PDF2WordError):
    """无效页码范围异常"""
    pass
```

- [ ] **Step 2: 修改 validate_input 函数**

将 `validate_input` 函数改为抛出异常：

```python
def validate_input(input_path: str) -> Path:
    """
    验证输入文件
    
    Args:
        input_path: 输入文件路径
        
    Returns:
        Path: 验证后的文件路径
        
    Raises:
        FileNotFoundError: 文件不存在
        InvalidPDFError: 文件格式错误
    """
    path = Path(input_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    if path.suffix.lower() != '.pdf':
        raise InvalidPDFError(f"文件格式错误: 需要PDF文件，当前为 {path.suffix}")
    
    return path
```

- [ ] **Step 3: 修改 parse_page_range 函数**

将 `parse_page_range` 函数改为抛出异常：

```python
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
```

- [ ] **Step 4: 修改 main 函数捕获异常**

```python
def main():
    args = parse_args()
    
    try:
        input_path = validate_input(args.input)
        pages = parse_page_range(args.pages)
    except PDF2WordError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    # ... 其余代码
```

- [ ] **Step 5: 验证语法**

```bash
python -m py_compile scripts/pdf2word.py
```

- [ ] **Step 6: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "refactor: unify error handling with exceptions in pdf2word.py"
```

---

### Task 2: 添加输出目录自动创建和 --force 参数

**Files:**
- Modify: `scripts/pdf2word.py`

**目标:** 输出目录不存在时自动创建，添加 --force 参数控制是否覆盖已存在的输出文件。

- [ ] **Step 1: 添加 --force 参数**

在 `parse_args` 函数中添加：

```python
parser.add_argument('-f', '--force', action='store_true',
                    help='强制覆盖已存在的输出文件')
```

- [ ] **Step 2: 修改 main 函数处理输出路径**

在 `main` 函数中，获取输出路径后添加：

```python
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.docx')
    
    # 检查输出文件是否存在
    if output_path.exists() and not args.force:
        print(f"错误: 输出文件已存在: {output_path}", file=sys.stderr)
        print(f"提示: 使用 --force 参数强制覆盖", file=sys.stderr)
        sys.exit(1)
    
    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 3: 更新帮助信息示例**

在 `parse_args` 的 epilog 中添加示例：

```python
epilog='''
示例:
  %(prog)s document.pdf
  %(prog)s document.pdf -o result.docx
  %(prog)s document.pdf --pages 1-5
  %(prog)s document.pdf --pages 1,3,5-10
  %(prog)s document.pdf --preset contract
  %(prog)s document.pdf -o result.docx --force
        '''
```

- [ ] **Step 4: 验证语法**

```bash
python -m py_compile scripts/pdf2word.py
```

- [ ] **Step 5: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "feat: add output directory creation and --force parameter"
```

---

### Task 3: 添加 --preset 预设模式

**Files:**
- Modify: `scripts/pdf2word.py`

**目标:** 添加预设模式参数，针对不同文档类型优化格式还原。

- [ ] **Step 1: 添加预设配置常量**

在文件顶部（导入后）添加：

```python
PRESETS = {
    'default': {
        'multi_processing': True,
    },
    'contract': {
        'multi_processing': False,
        'parse_lattice_table': True,
        'parse_stream_table': True,
        'max_border_width': 3.0,
        'connected_border_tolerance': 0.3,
        'line_separate_threshold': 3.0,
        'min_border_clearance': 1.0,
    },
    'table': {
        'multi_processing': True,
        'parse_lattice_table': True,
        'parse_stream_table': True,
        'float_image_ignorable_gap': 2.0,
        'extract_stream_table': True,
    },
    'text': {
        'multi_processing': True,
        'parse_lattice_table': False,
        'parse_stream_table': False,
        'new_paragraph_free_space_ratio': 0.7,
    },
}
```

- [ ] **Step 2: 添加 --preset 参数**

在 `parse_args` 函数中添加：

```python
parser.add_argument('--preset', choices=list(PRESETS.keys()), default='default',
                    help='预设模式: default(默认), contract(合同), table(表格), text(纯文本)')
```

- [ ] **Step 3: 修改 convert_pdf_to_docx 函数**

修改函数签名和实现：

```python
def convert_pdf_to_docx(input_path: Path, output_path: Path, pages: list = None,
                        preset: str = 'default', debug: bool = False) -> bool:
    """
    将PDF转换为Word文档
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出Word文件路径
        pages: 页码列表，None表示全部页面
        preset: 预设模式名称
        debug: 是否输出调试信息
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from pdf2docx import Converter
        
        convert_params = PRESETS.get(preset, PRESETS['default']).copy()
        convert_params['debug'] = debug
        
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
```

- [ ] **Step 4: 删除旧的 --mode 参数**

从 `parse_args` 中删除 `--mode` 参数（已被 --preset 替代）。

- [ ] **Step 5: 修改 main 函数调用**

```python
    preset_str = f"预设: {args.preset}" if args.preset != 'default' else ""
    print(f"正在转换: {input_path} -> {output_path} {preset_str}")
    
    if convert_pdf_to_docx(input_path, output_path, pages, args.preset, args.debug):
        print(f"转换完成: {output_path}")
    else:
        sys.exit(1)
```

- [ ] **Step 6: 验证语法**

```bash
python -m py_compile scripts/pdf2word.py
```

- [ ] **Step 7: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "feat: add --preset parameter for format optimization"
```

---

### Task 4: 更新 AGENTS.md 文档

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: 更新 pdf2word 命令说明**

修改 `AGENTS.md` 中的 PDF to Word 命令行：

```markdown
- PDF to Word: `python scripts/pdf2word.py input.pdf [-o output.docx] [--pages 1-5] [--preset contract] [--force] [--debug]`
```

- [ ] **Step 2: 提交**

```bash
git add AGENTS.md
git commit -m "docs: update pdf2word command with new options"
```

---

## 验收清单

- [ ] 错误处理统一为异常风格
- [ ] 输出目录不存在时自动创建
- [ ] `--force` 参数正常工作
- [ ] `--preset` 参数支持 default/contract/table/text 四种模式
- [ ] `--help` 显示所有新参数
- [ ] AGENTS.md 文档已更新
