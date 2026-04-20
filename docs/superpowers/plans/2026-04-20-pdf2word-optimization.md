# PDF转Word格式优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 优化pdf2word脚本，添加--mode和--debug参数，提升合同PDF格式还原度。

**Architecture:** 在现有脚本基础上添加新参数，修改convert_pdf_to_docx函数使用pdf2docx的高级参数。

**Tech Stack:** Python 3, pdf2docx, argparse

---

## 文件结构

```
scripts/
  pdf2word.py          # 修改：添加参数和优化转换逻辑
```

---

### Task 1: 添加--mode和--debug参数

**Files:**
- Modify: `scripts/pdf2word.py`

- [ ] **Step 1: 添加新参数到parse_args函数**

修改 `parse_args()` 函数，在 `--pages` 参数后添加：

```python
    parser.add_argument('--mode', choices=['normal', 'strict'], default='normal',
                        help='转换模式: normal(默认, 平衡速度与质量) / strict(严格模式, 更精确)')
    parser.add_argument('--debug', action='store_true',
                        help='输出调试信息')
    
    return parser.parse_args()
```

- [ ] **Step 2: 测试新参数**

Run: `.venv\Scripts\python scripts/pdf2word.py --help`

Expected: 帮助信息中显示 `--mode` 和 `--debug` 参数

Run: `.venv\Scripts\python scripts/pdf2word.py requirements.txt --mode strict --debug`

Expected: 不报错（验证参数解析正常）

- [ ] **Step 3: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "feat: add --mode and --debug arguments"
```

---

### Task 2: 实现转换参数优化

**Files:**
- Modify: `scripts/pdf2word.py`

- [ ] **Step 1: 修改convert_pdf_to_docx函数签名**

修改函数签名，添加 `mode` 和 `debug` 参数：

```python
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
```

- [ ] **Step 2: 添加转换参数构建逻辑**

在函数体内，`from pdf2docx import Converter` 之后，`cv = Converter` 之前添加：

```python
    try:
        from pdf2docx import Converter
        
        # 构建转换参数
        convert_params = {}
        
        if mode == 'strict':
            # 严格模式：更精确的格式还原
            convert_params = {
                'multi_processing': False,  # 单进程更稳定
                'debug': debug,
            }
        else:
            # 普通模式：平衡速度与质量
            convert_params = {
                'multi_processing': True,
                'debug': debug,
            }
        
        cv = Converter(str(input_path))
```

- [ ] **Step 3: 修改convert调用使用参数**

修改 `cv.convert()` 调用：

```python
        cv = Converter(str(input_path))
        try:
            if pages:
                cv.convert(str(output_path), pages=pages, **convert_params)
            else:
                cv.convert(str(output_path), **convert_params)
            return True
        finally:
            cv.close()
```

- [ ] **Step 4: 测试转换功能**

Run: `.venv\Scripts\python scripts/pdf2word.py --help`

Expected: 帮助信息正常显示

- [ ] **Step 5: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "feat: implement conversion mode and debug parameters"
```

---

### Task 3: 更新main函数传递新参数

**Files:**
- Modify: `scripts/pdf2word.py`

- [ ] **Step 1: 修改main函数调用convert_pdf_to_docx**

修改 `main()` 函数中的 `convert_pdf_to_docx` 调用：

```python
def main():
    args = parse_args()
    input_path = validate_input(args.input)
    pages = parse_page_range(args.pages)
    
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
```

- [ ] **Step 2: 测试完整功能**

Run: `.venv\Scripts\python scripts/pdf2word.py --help`

Expected: 帮助信息正常

- [ ] **Step 3: 提交**

```bash
git add scripts/pdf2word.py
git commit -m "feat: pass mode and debug to conversion function"
```

---

### Task 4: 更新AGENTS.md文档

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: 更新pdf2word命令说明**

修改 `AGENTS.md` 中 PDF to Word 命令行：

```markdown
- PDF to Word: `python scripts/pdf2word.py input.pdf [-o output.docx] [--pages 1-5] [--mode strict] [--debug]`
```

- [ ] **Step 2: 提交**

```bash
git add AGENTS.md
git commit -m "docs: update pdf2word command with new options"
```

---

## 验收清单

- [ ] `--help` 显示新参数说明
- [ ] `--mode normal` 正常工作
- [ ] `--mode strict` 正常工作
- [ ] `--debug` 不报错
- [ ] 转换功能正常
