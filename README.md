# Data Analysis Project

销售数据统计分析工具，支持多期数据对比分析，自动生成样式化Excel报表。

## 功能

- 多周期类型支持：年度、季度、月度、自定义时间范围
- 多Sheet/多文件Excel数据源支持
- 同比(YoY)分析
- 分组汇总（如督导人员汇总）
- 样式化Excel输出（蓝色表头、橙色总计、百分比格式）
- PDF转Word：支持多种预设模式优化格式还原

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

## 目录结构

```
data_analysis/
├── data/               # 输入Excel文件
│   └── 销售汇总表-*.xlsx
├── output/             # 输出报表（按日期分组）
├── scripts/            # 工具脚本
│   ├── run_analysis.py # 主分析脚本
│   ├── period_parser.py# 周期类型识别
│   ├── file_validator.py# 文件验证
│   ├── pdf2word.py     # PDF转Word
│   └── cleanup.py      # 清理脚本
├── docs/               # 文档
├── .opencode/          # OpenCode Skills
│   └── skills/
│       └── data-analysis-report/
├── Makefile            # Make 命令
├── requirements.txt
└── AGENTS.md           # 项目配置
```

## Skill: data-analysis-report

内置数据分析Skill，支持配置驱动的报表生成。

### 使用方式

```
用户: 分析这份销售数据 @data.xlsx
```

AI会自动：
1. 读取数据结构
2. 生成配置
3. 确认后执行
4. 输出样式化报表

### 配置示例

```yaml
data_source:
  type: multi_file
  files:
    - ./data/销售汇总表-2026.03.xlsx
    - ./data/销售汇总表-2026.02.xlsx

key_column: 点位名称
value_columns:
  - name: 总杯数
  - name: 总金额

periods:
  current: '2026.03'
  previous: '2026.02'
  current_file: '销售汇总表-2026.03'
  previous_file: '销售汇总表-2026.02'

analysis: [yoy]

group_by:
  column: 督导人员
  sheet_name: 督导人员汇总
  metrics: auto
  null_handling: ignore

output:
  dir: ./output
  title: 月度销售环比分析
```

### 配置说明

| 字段 | 说明 |
|------|------|
| `data_source.type` | `multi_sheet` 或 `multi_file` |
| `key_column` | 合并键列 |
| `value_columns` | 分析指标列 |
| `periods.current/previous` | 时期标签 |
| `group_by.column` | 分组列（可选） |
| `group_by.metrics` | `auto`=智能筛选含"总"的指标 |

## 依赖

- pandas
- numpy
- openpyxl
- pyyaml
- pdf2docx

## 许可

MIT
