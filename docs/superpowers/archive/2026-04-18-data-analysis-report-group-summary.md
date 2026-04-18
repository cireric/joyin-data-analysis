# Data Analysis Report Skill - Group Summary Extension

**Date:** 2026-04-18
**Status:** Approved

---

## Goal

Extend `data-analysis-report` skill to support group-by summary sheets (e.g., supervisor summary) in addition to point-level summary.

---

## Current State

| Feature | Status |
|---------|--------|
| Single sheet output (point summary) | ✅ Implemented |
| Multi-sheet/multi-file data source | ✅ Implemented |
| YoY/MoM comparison | ✅ Implemented |
| Group-by summary | ❌ Missing |

---

## New Configuration

### `group_by` Block (Optional)

```yaml
group_by:
  column: 督导人员              # Column to group by
  sheet_name: 督导人员汇总       # Output sheet name (default: "{column}汇总")
  metrics: auto                # auto | list of metric names
  null_handling: ignore        # ignore | unassigned
```

### Field Descriptions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `column` | string | Required | Column name to group by (e.g., 督导人员) |
| `sheet_name` | string | `{column}汇总` | Output sheet name |
| `metrics` | string/list | `auto` | `auto` = smart filter, or explicit list |
| `null_handling` | string | `ignore` | `ignore` = skip nulls, `unassigned` = group as "未分配" |

### Smart Filter Logic

When `metrics: auto`:
1. Filter `value_columns` for columns containing "总" (e.g., 总杯数, 总金额)
2. If no match, use all `value_columns`

---

## Output Behavior

| Config | Output |
|--------|--------|
| No `group_by` | Single sheet: 点位汇总 |
| Has `group_by` | Two sheets: 点位汇总 + {sheet_name} |

---

## Example Configuration

```yaml
data_source:
  type: multi_file
  files:
    - ./data/销售汇总表-2026.03.xlsx
    - ./data/销售汇总表-2026.02.xlsx

key_column: 点位名称
value_columns:
  - name: 线上杯数
  - name: 线下杯数
  - name: 线上金额
  - name: 线下金额
  - name: 测试杯
  - name: 总杯数
  - name: 总金额

periods:
  current: '销售汇总表-2026.03'
  previous: '销售汇总表-2026.02'

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

---

## Implementation Changes

### 1. `templates/config.yaml`

Add `group_by` section with comments.

### 2. `scripts/generate_report.py`

- Add `generate_group_summary()` function
- Modify `generate_report()` to check for `group_by` config
- Add second sheet if `group_by` is present
- Apply smart filter logic for metrics

### 3. `SKILL.md`

- Document `group_by` configuration
- Update workflow diagram
- Add usage example with group summary

---

## Future Extensions

Reserved for future:
- `group_by.column: 区域` - when data has region column
- `group_by.column: 合作商` - when data has partner column
- Multiple `group_by` blocks for multiple summary sheets

---

## Testing

Test cases:
1. No `group_by` → single sheet output
2. `group_by` with `metrics: auto` → smart filter works
3. `group_by` with explicit metrics list → uses specified metrics
4. `null_handling: ignore` → nulls excluded from group summary
5. `null_handling: unassigned` → nulls grouped as "未分配"
