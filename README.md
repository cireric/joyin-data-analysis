# Data Analysis Project

销售数据统计分析工具，支持多期数据对比分析，自动生成样式化Excel报表。

## 功能

- 多周期类型支持：年度、季度、月度、自定义时间范围
- 多Sheet/多文件Excel数据源支持
- 同比(YoY)分析
- 分组汇总（如督导人员汇总）
- 样式化Excel输出（蓝色表头、橙色总计、百分比格式）
- PDF转Word：支持多种预设模式优化格式还原
- URL转Markdown：抓取网页内容并转换为Markdown格式

## 快速开始

### 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix
pip install -r requirements.txt
```

### 运行分析

使用 Make 命令（推荐）：

```bash
# 年度分析
make analyze c=2026 p=2025

# 季度分析
make analyze c=2026Q1 p=2025Q1

# 月度分析
make analyze c=2026.03 p=2026.02

# 自定义时间范围
make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12
```

直接调用脚本：

```bash
.venv\Scripts\python.exe scripts\run_analysis.py -c 2026.03 -p 2026.02

# 查看帮助
.venv\Scripts\python.exe scripts\run_analysis.py --help
```

### 清理输出

```bash
make clean

# 或直接调用
.venv\Scripts\python.exe scripts\cleanup.py --dry-run  # 预览
.venv\Scripts\python.exe scripts\cleanup.py            # 执行
.venv\Scripts\python.exe scripts\cleanup.py --keep-days 7  # 保留最近7天
```

### PDF转Word

将PDF文件转换为可编辑的Word文档，支持多种预设模式优化格式还原：

```bash
# 基本转换
python scripts/pdf2word.py input.pdf

# 指定输出文件
python scripts/pdf2word.py input.pdf -o output.docx

# 转换指定页码
python scripts/pdf2word.py input.pdf --pages 1-5
python scripts/pdf2word.py input.pdf --pages 1,3,5-10

# 使用预设模式（优化格式还原）
python scripts/pdf2word.py contract.pdf --preset contract  # 合同文档
python scripts/pdf2word.py report.pdf --preset table       # 表格为主
python scripts/pdf2word.py article.pdf --preset text       # 纯文本文档

# 强制覆盖已存在的输出文件
python scripts/pdf2word.py input.pdf -o output.docx --force

# 调试模式
python scripts/pdf2word.py input.pdf --debug
```

**预设模式说明：**

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| `default` | 普通文档 | 平衡速度与质量 |
| `contract` | 合同/协议 | 精确表格边框、严格对齐 |
| `table` | 表格为主 | 增强表格解析、忽略浮动图片 |
| `text` | 纯文本文档 | 增强段落解析、忽略表格 |

### URL转Markdown

抓取网页内容并转换为Markdown格式，支持单篇文章和列表页批量抓取：

```bash
# 单篇文章
python scripts/url2md.py "https://mp.weixin.qq.com/s/xxx"

# 列表页（批量抓取）
python scripts/url2md.py "https://mp.weixin.qq.com/mp/profile_ext?action=home&..."

# 指定输出目录
python scripts/url2md.py <url> --output misc/articles/

# 下载图片到本地
python scripts/url2md.py <url> --download-images

# 限制抓取数量
python scripts/url2md.py <url> --limit 10

# 断点续传
python scripts/url2md.py <url> --resume --state state.json

# 自定义延迟
python scripts/url2md.py <url> --delay 3 --max-delay 8
```

**注意：** 首次使用需要确保系统已安装 Chrome 浏览器。

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 文章或列表页URL | 必填 |
| `--output` | 输出目录 | `misc/` |
| `--filename` | 文件名（仅单篇有效） | 自动生成 |
| `--download-images` | 下载图片到本地 | 否 |
| `--images-dir` | 图片保存目录 | `output/images/` |
| `--limit` | 列表页最大抓取数 | 无限制 |
| `--delay` | 基础延迟（秒） | 2 |
| `--max-delay` | 最大延迟（秒） | 5 |
| `--resume` | 断点续传 | 否 |
| `--state` | 状态文件路径 | `url2md-state.json` |

**支持平台：**
- 微信公众号
- 知乎专栏
- 简书
- 通用网页（自动识别）

### Markdown to PDF

Convert Markdown files to PDF documents.

```bash
# Single file
python scripts/md2pdf.py input.md

# Specify output path
python scripts/md2pdf.py input.md -o output.pdf

# Generate table of contents
python scripts/md2pdf.py input.md --toc

# Specify PDF engine
python scripts/md2pdf.py input.md --pdf-engine xelatex

# Force overwrite
python scripts/md2pdf.py input.md --force

# Batch convert folder
python scripts/md2pdf.py --batch docs/

# Batch with output directory
python scripts/md2pdf.py --batch docs/ --output pdfs/

# Recursive batch convert
python scripts/md2pdf.py --batch docs/ --recursive

# Debug mode
python scripts/md2pdf.py input.md --debug
```

**Features:**
- Automatic Chinese content detection with appropriate engine and font selection
- YAML frontmatter support for metadata extraction (title, author, date)
- Automatic PDF engine detection
- Table of contents generation
- Batch conversion with progress display

**Dependencies:**
- pandoc (required)
- PDF engine (any one): weasyprint (default), xelatex, wkhtmltopdf, pdflatex

## 目录结构

```
data_analysis/
├── data/               # 输入Excel文件
│   └── 销售汇总表-*.xlsx
├── output/             # 输出报表（按日期分组）
├── src/
│   ├── data_analysis/  # 数据分析模块
│   │   ├── loader.py   # 数据加载与验证
│   │   ├── analyzer.py # 数据分析函数
│   │   ├── report.py   # 报表生成
│   │   └── styler.py   # Excel样式
│   └── data_crawl/     # 网页抓取模块
│       ├── api.py      # 同步API入口
│       ├── extractor.py # 内容提取
│       ├── selectors.py # 平台选择器配置
│       ├── downloader.py # 图片下载
│       ├── browser.py  # 浏览器管理
│       └── utils.py    # 工具函数
├── scripts/            # CLI入口脚本
│   ├── run_analysis.py # 主分析脚本
│   ├── pdf2word.py     # PDF转Word
│   ├── md2word.py      # Markdown转Word
│   ├── md2pdf.py       # Markdown转PDF
│   ├── url2md.py       # URL转Markdown
│   ├── cleanup.py      # 清理脚本
│   └── lib/            # 库模块
│       ├── converter_base.py # 转换器基础模块
│       ├── period_parser.py  # 周期解析器
│       └── file_validator.py # 文件验证器
├── .opencode/skills/   # OpenCode Skills
│   └── url2md/         # URL转Markdown Skill
├── tests/              # 单元测试
├── docs/               # 文档
├── Makefile            # Make 命令
├── requirements.txt
└── AGENTS.md           # 项目配置
```

## 依赖

- pandas - 数据处理
- numpy - 数值计算
- openpyxl - Excel读写
- pyyaml - YAML配置
- pdf2docx - PDF转Word
- pypandoc - Markdown转Word
- playwright - 网页抓取
- aiohttp - 异步HTTP请求
- aiofiles - 异步文件操作
- pytest - 测试框架
- pytest-asyncio - 异步测试支持

## 许可

MIT
