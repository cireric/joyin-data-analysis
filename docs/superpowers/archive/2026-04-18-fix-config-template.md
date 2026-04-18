# templates/config.yaml 配置修复计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 templates/config.yaml 中的列名配置，使其与实际 Excel 数据结构匹配

**Architecture:** 更新 value_columns 为实际存在的列名，并完善配置模板

**Tech Stack:** YAML 配置文件

---

## 问题分析

**当前配置 (templates/config.yaml):**
```yaml
value_columns:
  - name: 购买杯数    # 不存在
  - name: 销售金额    # 不存在
```

**实际 Excel 列名 (销售汇总表-2026.03.xlsx):**
```
机器编号, 点位名称, 线上杯数, 线上金额, 线下杯数, 线下金额, 
测试杯, 免费杯, 兑换码赠送杯, 总杯数, 总金额, 
线上销售比例, 线下销售比例, 督导人员
```

---

## Task 1: 更新 templates/config.yaml 配置

**Files:**
- Modify: `.opencode/skills/data-analysis-report/templates/config.yaml`

- [ ] **Step 1: 更新 value_columns 和完善配置**

将整个文件替换为:

```yaml
# Data Analysis Report Configuration
# Template for generating YoY/MoM analysis reports

# Data source configuration
data_source:
  type: multi_file           # multi_sheet | multi_file
  files:                     # File paths for multi_file type
    - ./data/销售汇总表-2026.03.xlsx
    - ./data/销售汇总表-2026.02.xlsx
  # For multi_sheet type:
  # type: multi_sheet
  # path: ./data/source.xlsx
  # sheets: ['2026.03', '2026.02']

# Column configuration
key_column: 点位名称          # Column to merge on (must exist in all periods)
value_columns:               # Columns to analyze
  - name: 总杯数
  - name: 总金额

# Period configuration
periods:
  current: '2026.03'         # Current period label (used in column names)
  previous: '2026.02'        # Previous period label (used in column names)
  current_file: '销售汇总表-2026.03'
  previous_file: '销售汇总表-2026.02'

# Analysis types
analysis:
  - yoy                      # Year-over-year comparison
  # - mom                    # Month-over-month comparison (optional)

# Output configuration
output:
  dir: ./output              # Output directory
  title: 月度销售环比分析      # Report title (used for sheet name and file name)

# Group summary configuration (optional)
group_by:
  column: 督导人员            # Column to group by
  sheet_name: 督导人员汇总     # Output sheet name (default: "{column}汇总")
  metrics: auto              # auto = smart filter (columns with "总"), or explicit list
  null_handling: ignore      # ignore = skip nulls, unassigned = group as "未分配"
```

- [ ] **Step 2: 验证 YAML 语法**

Run: `.venv\Scripts\python.exe -c "import yaml; yaml.safe_load(open('.opencode/skills/data-analysis-report/templates/config.yaml', encoding='utf-8')); print('YAML valid')"`
Expected: `YAML valid`

- [ ] **Step 3: 使用更新后的配置生成报表验证**

Run: `.venv\Scripts\python.exe .opencode/skills/data-analysis-report/scripts/generate_report.py .opencode/skills/data-analysis-report/templates/config.yaml`
Expected: 报表已生成

- [ ] **Step 4: Commit**

```bash
git add .opencode/skills/data-analysis-report/templates/config.yaml
git commit -m "fix: update templates/config.yaml to match actual Excel column names"
```

---

## Task 2: 清理测试配置文件

**Files:**
- Remove: `data/config.yaml` (测试时创建的临时文件)

- [ ] **Step 1: 删除测试配置**

```bash
git rm data/config.yaml
```

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: remove test config file"
```

---

## 修复总结

| 任务 | 内容 |
|------|------|
| Task 1 | 更新 templates/config.yaml 列名配置 |
| Task 2 | 清理临时测试文件 |
