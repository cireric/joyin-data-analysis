# Data Analysis Project

销售数据统计分析工具，支持多期数据对比分析，自动生成样式化Excel报表。

## 功能

- 多Sheet/多文件Excel数据源支持
- 同比(YoY)分析
- 分组汇总（如督导人员汇总）
- 样式化Excel输出（蓝色表头、橙色总计、百分比格式）

## 快速开始

### 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix
pip install -r requirements.txt
```

### 运行分析

```bash
.venv\Scripts\python.exe data_analysis_202603.py
```

### 清理输出

```bash
# 预览将删除的文件
.venv\Scripts\python.exe scripts\cleanup.py --dry-run

# 执行删除
.venv\Scripts\python.exe scripts\cleanup.py

# 保留最近7天的报表
.venv\Scripts\python.exe scripts\cleanup.py --keep-days 7
```

## 目录结构

```
data_analysis/
├── data/               # 输入Excel文件
├── output/             # 输出报表（按日期分组）
├── scripts/            # 工具脚本
│   └── cleanup.py      # 清理脚本
├── docs/               # 文档
├── .opencode/          # OpenCode Skills
│   └── skills/
│       └── data-analysis-report/
├── data_analysis_202603.py  # 主入口
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

## 许可

MIT
