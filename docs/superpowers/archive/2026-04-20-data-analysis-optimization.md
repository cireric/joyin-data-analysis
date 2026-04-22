# 数据分析程序最小可行优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 统一错误处理风格、拆分大函数，使数据分析程序更健壮可维护。

**Architecture:** 保持现有架构，仅做最小改动：统一异常处理风格、拆分 75 行大函数为 3 个职责单一的小函数。

**Tech Stack:** Python 3, pandas, openpyxl

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `scripts/file_validator.py` | 修改 | `validate()` 改为抛异常 |
| `scripts/run_analysis.py` | 修改 | 拆分函数 + 修改调用方式 |

---

### Task 1: 统一错误处理 - file_validator.py

**Files:**
- Modify: `scripts/file_validator.py`

- [ ] **Step 1: 修改 validate 方法签名和实现**

将返回元组改为抛异常，替换整个 `validate` 方法：

```python
    @classmethod
    def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> None:
        """
        验证数据文件是否存在
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Raises:
            FileNotFoundError: 当数据文件不存在时抛出
        """
        current_path = cls.DATA_DIR / current.file_name
        previous_path = cls.DATA_DIR / previous.file_name
        
        if not current_path.exists():
            raise FileNotFoundError(f"未找到当前期数据文件: data/{current.file_name}")
        
        if not previous_path.exists():
            raise FileNotFoundError(f"未找到对比期数据文件: data/{previous.file_name}")
```

- [ ] **Step 2: 移除不再需要的 Tuple, List 导入**

修改文件顶部导入（第 6 行），删除 `Tuple, List`：

```python
from pathlib import Path

from period_parser import PeriodInfo
```

- [ ] **Step 3: 验证语法**

```bash
python -m py_compile scripts/file_validator.py
```
Expected: 无输出（成功）

- [ ] **Step 4: 提交**

```bash
git add scripts/file_validator.py
git commit -m "refactor: change FileValidator.validate to raise exception"
```

---

### Task 2: 统一错误处理 - run_analysis.py 调用方

**Files:**
- Modify: `scripts/run_analysis.py:209-213`

- [ ] **Step 1: 修改 validate 调用为 try/except**

将：
```python
    valid, errors = FileValidator.validate(current_info, previous_info)
    if not valid:
        for error in errors:
            print(error)
        sys.exit(1)
```

改为：
```python
    try:
        FileValidator.validate(current_info, previous_info)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
```

- [ ] **Step 2: 验证语法**

```bash
python -m py_compile scripts/run_analysis.py
```
Expected: 无输出（成功）

- [ ] **Step 3: 提交**

```bash
git add scripts/run_analysis.py
git commit -m "refactor: use try/except for FileValidator.validate"
```

---

### Task 3: 拆分 generate_report_from_config 函数

**Files:**
- Modify: `scripts/run_analysis.py:84-158`

- [ ] **Step 1: 添加 load_and_validate 函数**

在 `create_config` 函数之后、`generate_report_from_config` 函数之前添加：

```python
def load_and_validate(config: dict) -> dict:
    """加载数据并验证"""
    data = load_data(config)
    validate_data(data, config['periods'], config['key_column'], config['value_columns'])
    return data
```

- [ ] **Step 2: 添加 process_data 函数**

```python
def process_data(data: dict, config: dict) -> pd.DataFrame:
    """处理数据：合并、填充、计算、添加总计"""
    merged = merge_periods(data, config['periods'], config['key_column'], config['value_columns'])
    merged = fill_missing_values(merged, config['key_column'], config['value_columns'])
    result = calculate_analysis(merged, config['value_columns'], config['analysis'])
    result = add_totals(result, config['key_column'], config['value_columns'], config['analysis'])
    return result
```

- [ ] **Step 3: 添加 export_report 函数**

```python
def export_report(result: pd.DataFrame, data: dict, config: dict) -> tuple:
    """导出报表：格式化、样式、保存"""
    reordered_columns = reorder_value_columns(config['value_columns'])
    
    output_cols = [config['key_column']]
    for vc in reordered_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        output_cols.extend([f"{col_name}_previous", f"{col_name}_current", f"{col_name}_yoy"])
    
    result = result[output_cols]
    
    rename_map = {config['key_column']: config['key_column']}
    for vc in config['value_columns']:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        prev_label = config['periods']['previous']
        curr_label = config['periods']['current']
        rename_map[f"{col_name}_previous"] = f"{prev_label}{col_name}"
        rename_map[f"{col_name}_current"] = f"{curr_label}{col_name}"
        rename_map[f"{col_name}_yoy"] = f"{col_name}同比"
    
    result.rename(columns=rename_map, inplace=True)
    
    wb = Workbook()
    ws = wb.active
    ws.title = config['output']['title']
    
    for r in dataframe_to_rows(result, index=False, header=True):
        ws.append(r)
    
    style_workbook(ws, reordered_columns, config['analysis'])
    
    group_result = None
    if 'group_by' in config and config['group_by']:
        group_config = config['group_by']
        group_col = group_config['column']
        sheet_name = group_config.get('sheet_name', f"{group_col}汇总")
        metrics = filter_group_metrics(config['value_columns'], group_config.get('metrics', 'auto'))
        
        group_result = generate_group_summary(
            data, config['periods'], group_config, config['value_columns'], config['analysis']
        )
        
        ws2 = wb.create_sheet(sheet_name)
        for r in dataframe_to_rows(group_result, index=False, header=True):
            ws2.append(r)
        
        style_group_sheet(ws2, metrics)
    
    date_dir = datetime.now().strftime('%Y%m%d')
    output_dir = Path(config['output']['dir']) / date_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    time_str = datetime.now().strftime('%H%M%S')
    safe_title = sanitize_filename(config['output']['title'])
    output_file = output_dir / f"{safe_title}_{time_str}.xlsx"
    wb.save(output_file)
    
    return str(output_file), len(result) - 1, len(group_result) - 1 if group_result is not None else 0
```

- [ ] **Step 4: 简化 generate_report_from_config 函数**

将原 75 行函数替换为：

```python
def generate_report_from_config(config: dict) -> tuple:
    """根据配置生成报表"""
    data = load_and_validate(config)
    result = process_data(data, config)
    return export_report(result, data, config)
```

- [ ] **Step 5: 验证语法**

```bash
python -m py_compile scripts/run_analysis.py
```
Expected: 无输出（成功）

- [ ] **Step 6: 提交**

```bash
git add scripts/run_analysis.py
git commit -m "refactor: split generate_report_from_config into 3 functions"
```

---

### Task 4: 集成测试验证

**Files:**
- 无文件修改，仅验证

- [ ] **Step 1: 运行分析命令验证**

```bash
make analyze c=2026.03 p=2026.02
```
Expected: 报表成功生成，输出文件路径

- [ ] **Step 2: 确认输出文件存在**

检查 `output/` 目录下生成的 `.xlsx` 文件。

---

## 自检清单

- [x] Spec 覆盖：所有设计要求都有对应任务
- [x] 无占位符：所有代码完整
- [x] 类型一致：函数签名匹配
