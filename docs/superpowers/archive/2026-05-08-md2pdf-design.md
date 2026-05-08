# md2pdf 工具设计文档

## 概述

创建 Markdown 转 PDF 工具 `scripts/md2pdf.py`，与现有的 `md2word.py` 和 `pdf2word.py` 形成完整的文档转换工具链。

## 需求确认

| 维度 | 决策 |
|------|------|
| 技术栈 | Pandoc 路线（pypandoc + pandoc） |
| 样式控制 | 简单模式，默认样式 |
| PDF 引擎 | 自动检测（weasyprint → xelatex → wkhtmltopdf → pdflatex） |
| 默认引擎 | weasyprint（写入 requirements.txt） |
| 中文支持 | 自动检测并处理，自动选择引擎和字体 |
| CLI 参数 | 最小参数集，与 md2word.py 一致 |
| 错误处理 | 友好提示 + 降级方案 + 安装指引 |
| 输出命名 | 同名替换后缀 |
| 依赖检查 | 懒检查 + 详细指引 |
| 代码复用 | 提取公共模块 `scripts/lib/converter_base.py` |
| 测试策略 | 单元测试 + 集成测试 |
| 异常设计 | 独立异常类 |
| 文档支持 | CLI 帮助 + README.md 更新 |
| Makefile | 添加独立命令 |
| PDF 元数据 | 从 Markdown frontmatter 提取 |
| 调试模式 | 基础调试（`--debug`） |
| 性能优化 | 不优化，直接转换 |
| 版本号 | 独立版本号（md2pdf 1.0） |

## 架构设计

### 目录结构

```
data_analysis/
├── scripts/
│   ├── lib/                     # 新增：脚本公共库
│   │   ├── __init__.py
│   │   └── converter_base.py    # 公共转换逻辑
│   ├── md2word.py               # 重构：使用 lib.converter_base
│   ├── md2pdf.py                # 新增：Markdown 转 PDF
│   ├── pdf2word.py              # 可选重构
│   └── ...
├── tests/
│   ├── fixtures/                # 测试文件
│   │   ├── simple.md
│   │   ├── chinese.md
│   │   ├── with_frontmatter.md
│   │   └── with_toc.md
│   ├── test_converter_base.py   # 新增：公共模块测试
│   ├── test_md2pdf.py           # 新增：单元测试
│   └── test_md2pdf_integration.py # 新增：集成测试
├── requirements.txt             # 更新：添加 weasyprint
├── Makefile                     # 更新：添加 md2pdf 命令
└── README.md                    # 更新：添加使用说明
```

### 职责边界

- `src/data_analysis/` → 数据分析核心业务（不涉及）
- `scripts/lib/` → 文档转换工具公共逻辑
- `scripts/*.py` → CLI 入口

## 模块设计

### scripts/lib/converter_base.py

公共函数模块，提供以下功能：

```python
def validate_input(input_path: str, allowed_extensions: tuple) -> Path:
    """验证输入文件存在性和扩展名"""

def resolve_output(input_path: Path, output_arg: str, force: bool, default_suffix: str) -> Path:
    """解析输出路径，处理覆盖检查"""

def find_pandoc() -> Optional[str]:
    """查找 pandoc 可执行文件"""

def detect_chinese(text: str) -> bool:
    """检测文本是否包含中文字符"""

def parse_frontmatter(content: str) -> dict:
    """解析 Markdown YAML frontmatter"""

def get_available_pdf_engines() -> list[str]:
    """检测系统中可用的 PDF 引擎"""

def get_chinese_font() -> Optional[str]:
    """获取系统可用的中文字体"""
```

### scripts/md2pdf.py

主程序模块，包含：

**异常类：**
```python
class Md2PdfError(Exception):
    """基础异常"""

class InputFileNotFoundError(Md2PdfError):
    """文件不存在"""

class InvalidMarkdownError(Md2PdfError):
    """无效 Markdown 文件"""

class ConversionError(Md2PdfError):
    """转换失败"""

class DependencyError(Md2PdfError):
    """依赖缺失"""

class EngineNotFoundError(Md2PdfError):
    """PDF 引擎未找到"""
```

**核心函数：**
```python
def convert_md_to_pdf(input_path: Path, output_path: Path,
                      pdf_engine: str = None, toc: bool = False,
                      debug: bool = False) -> bool:
    """
    转换流程：
    1. 读取 Markdown 内容
    2. 解析 frontmatter 提取元数据
    3. 检测是否包含中文
    4. 自动选择 PDF 引擎（或使用用户指定）
    5. 构建转换参数（引擎、字体、元数据）
    6. 调用 pypandoc 转换
    7. 返回结果
    """

def select_pdf_engine(content: str, user_engine: str = None, debug: bool = False) -> str:
    """
    选择逻辑：
    1. 用户指定引擎 → 直接使用
    2. 检测到中文 → 优先 xelatex
    3. 无中文 → 按优先级自动检测可用引擎
    4. 所有引擎不可用 → 抛出 EngineNotFoundError
    """

def generate_install_guide() -> str:
    """生成详细的引擎安装指引"""
```

**引擎优先级：**
```python
PDF_ENGINE_PRIORITY = ['weasyprint', 'xelatex', 'wkhtmltopdf', 'pdflatex']
```

## CLI 参数设计

```bash
# 基础用法
python scripts/md2pdf.py input.md

# 指定输出路径
python scripts/md2pdf.py input.md -o output.pdf

# 指定 PDF 引擎
python scripts/md2pdf.py input.md --pdf-engine xelatex

# 生成目录
python scripts/md2pdf.py input.md --toc

# 强制覆盖
python scripts/md2pdf.py input.md --force

# 调试模式
python scripts/md2pdf.py input.md --debug

# 查看版本
python scripts/md2pdf.py --version
```

**参数定义：**
```python
parser.add_argument('input', help='输入Markdown文件路径')
parser.add_argument('-o', '--output', help='输出PDF文件路径 (默认: 输入文件名.pdf)')
parser.add_argument('--pdf-engine', help='PDF引擎 (weasyprint/xelatex/wkhtmltopdf/pdflatex)')
parser.add_argument('--toc', action='store_true', help='生成目录')
parser.add_argument('--debug', action='store_true', help='输出调试信息')
parser.add_argument('-f', '--force', action='store_true', help='强制覆盖已存在的输出文件')
parser.add_argument('--version', action='version', version='md2pdf 1.0')
```

## 错误处理

### 引擎缺失错误提示

```
错误: 未找到可用的 PDF 引擎

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
```

### Pandoc 缺失错误提示

```
错误: 未找到 pandoc

请安装 pandoc:
- Windows: https://pandoc.org/installing.html
- 或运行: winget install --id JohnMacFarlane.Pandoc

安装后重新运行此命令。
```

### 字体缺失警告

```
警告: 未找到中文字体，使用系统默认字体

建议安装以下字体之一：
- SimSun (宋体)
- Microsoft YaHei (微软雅黑)
- FangSong (仿宋)
```

## 测试策略

### 单元测试 (tests/test_md2pdf.py)

```python
- test_validate_input_valid()           # 有效输入
- test_validate_input_not_found()       # 文件不存在
- test_validate_input_invalid_ext()     # 无效扩展名
- test_resolve_output_default()         # 默认输出路径
- test_resolve_output_custom()          # 自定义输出路径
- test_resolve_output_force()           # 强制覆盖
- test_detect_chinese_true()            # 检测中文
- test_detect_chinese_false()           # 无中文
- test_parse_frontmatter_valid()        # 解析 frontmatter
- test_parse_frontmatter_empty()        # 无 frontmatter
- test_select_pdf_engine_user_specified() # 用户指定引擎
- test_select_pdf_engine_chinese()      # 中文文档选引擎
- test_select_pdf_engine_auto()         # 自动选择引擎
```

### 集成测试 (tests/test_md2pdf_integration.py)

```python
# 测试文件
tests/fixtures/
├── simple.md              # 简单英文文档
├── chinese.md             # 中文文档
├── with_frontmatter.md    # 带 frontmatter
└── with_toc.md            # 需要目录

# 测试用例
- test_convert_simple()              # 基础转换
- test_convert_chinese()             # 中文转换
- test_convert_with_frontmatter()    # 元数据提取
- test_convert_with_toc()            # 目录生成
- test_convert_output_exists()       # 输出已存在
```

## 文件变更清单

### 新增文件

1. `scripts/lib/__init__.py`
2. `scripts/lib/converter_base.py`
3. `scripts/md2pdf.py`
4. `tests/test_converter_base.py`
5. `tests/test_md2pdf.py`
6. `tests/test_md2pdf_integration.py`
7. `tests/fixtures/simple.md`
8. `tests/fixtures/chinese.md`
9. `tests/fixtures/with_frontmatter.md`
10. `tests/fixtures/with_toc.md`

### 修改文件

1. `scripts/md2word.py` - 重构使用 lib.converter_base
2. `requirements.txt` - 添加 weasyprint>=60.0
3. `Makefile` - 添加 md2pdf 命令
4. `README.md` - 添加 md2pdf 使用说明

## 依赖更新

**requirements.txt 新增：**
```
weasyprint>=60.0
```

**已有依赖（复用）：**
```
pypandoc>=1.11
```

## Makefile 集成

```makefile
md2pdf:
	@python scripts/md2pdf.py $(ARGS)
```

## README.md 更新内容

在"文档转换工具"章节添加：

```markdown
### Markdown 转 PDF

将 Markdown 文件转换为 PDF 文档。

```bash
# 基础用法
python scripts/md2pdf.py input.md

# 指定输出路径
python scripts/md2pdf.py input.md -o output.pdf

# 生成目录
python scripts/md2pdf.py input.md --toc

# 指定 PDF 引擎
python scripts/md2pdf.py input.md --pdf-engine xelatex

# 强制覆盖
python scripts/md2pdf.py input.md --force

# 调试模式
python scripts/md2pdf.py input.md --debug
```

**特性：**
- 自动检测中文内容并选择合适的引擎和字体
- 支持 YAML frontmatter 提取元数据（标题、作者、日期）
- 自动检测系统中可用的 PDF 引擎
- 支持生成目录

**依赖：**
- pandoc（必需）
- PDF 引擎（任选其一）：weasyprint（默认）、xelatex、wkhtmltopdf、pdflatex
```

## 实现优先级

1. **Phase 1: 公共模块**
   - 创建 `scripts/lib/converter_base.py`
   - 提取公共函数
   - 编写单元测试

2. **Phase 2: 核心功能**
   - 创建 `scripts/md2pdf.py`
   - 实现转换逻辑
   - 实现引擎检测
   - 实现中文支持

3. **Phase 3: 重构现有代码**
   - 重构 `scripts/md2word.py` 使用公共模块

4. **Phase 4: 测试与文档**
   - 编写集成测试
   - 更新 README.md
   - 更新 Makefile
   - 更新 requirements.txt
