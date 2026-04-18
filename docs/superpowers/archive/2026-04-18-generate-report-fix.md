# generate_report.py 安全与质量修复计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 generate_report.py 中的安全隐患、数据边界问题和逻辑漏洞

**Architecture:** 添加验证函数模块，修改现有函数增加边界检查，修正 fill_missing_values 逻辑

**Tech Stack:** Python 3.x, pandas, openpyxl

---

## 文件结构

**修改文件:**
- `.opencode/skills/data-analysis-report/scripts/generate_report.py` - 主文件，添加验证和修复逻辑

**新增函数:**
- `validate_path()` - 路径安全验证
- `validate_config()` - 配置完整性验证
- `validate_data()` - 数据有效性验证
- `sanitize_filename()` - 文件名清理

---

## Task 1: 添加路径安全验证函数

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py:26-31` (在 load_config 之后)

- [ ] **Step 1: 添加路径验证和文件名清理函数**

在 L26 (try/except 块后) 添加:

```python
def validate_path(path: str, base_dir: str = None) -> Path:
    """
    Validate path is safe and within expected directory.
    
    Args:
        path: Path to validate
        base_dir: Optional base directory to restrict access
        
    Returns:
        Resolved Path object
        
    Raises:
        ValueError: If path is invalid or outside base_dir
    """
    resolved = Path(path).resolve()
    
    if base_dir:
        base = Path(base_dir).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError(f"Path '{path}' is outside allowed directory '{base_dir}'")
    
    if not resolved.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    
    return resolved


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename by removing dangerous characters.
    
    Args:
        name: Original filename
        
    Returns:
        Safe filename string
    """
    import re
    sanitized = re.sub(r'[<>:"/\\|?*\.\.]', '_', name)
    sanitized = sanitized.strip()
    return sanitized if sanitized else 'output'
```

- [ ] **Step 2: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: add path validation and filename sanitization functions"
```

---

## Task 2: 添加配置验证函数

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py` (在 validate_path 之后)

- [ ] **Step 1: 添加配置验证函数**

```python
def validate_config(config: dict) -> None:
    """
    Validate configuration has all required fields.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If required fields are missing
    """
    required_keys = ['data_source', 'periods', 'key_column', 'value_columns', 'analysis', 'output']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")
    
    if 'current' not in config['periods'] or 'previous' not in config['periods']:
        raise ValueError("Config 'periods' must have 'current' and 'previous' keys")
    
    if 'title' not in config['output'] or 'dir' not in config['output']:
        raise ValueError("Config 'output' must have 'title' and 'dir' keys")
    
    if not config['value_columns']:
        raise ValueError("Config 'value_columns' cannot be empty")
```

- [ ] **Step 2: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: add config validation function"
```

---

## Task 3: 添加数据验证函数

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py` (在 validate_config 之后)

- [ ] **Step 1: 添加数据验证函数**

```python
def validate_data(data: dict, periods: dict, key_column: str, value_columns: list) -> None:
    """
    Validate loaded data has required periods and columns.
    
    Args:
        data: Dict of period DataFrames
        periods: Period labels
        key_column: Key column name
        value_columns: List of value column configs
        
    Raises:
        ValueError: If data is invalid
    """
    current_key = periods['current']
    previous_key = periods['previous']
    
    if current_key not in data:
        raise ValueError(f"Current period data not found: '{current_key}'")
    if previous_key not in data:
        raise ValueError(f"Previous period data not found: '{previous_key}'")
    
    for period_key in [current_key, previous_key]:
        df = data[period_key]
        
        if df.empty:
            raise ValueError(f"Empty dataset for period: '{period_key}'")
        
        if key_column not in df.columns:
            raise ValueError(f"Key column '{key_column}' not found in period '{period_key}'")
        
        missing_cols = []
        for vc in value_columns:
            col_name = vc['name'] if isinstance(vc, dict) else vc
            if col_name not in df.columns:
                missing_cols.append(col_name)
        
        if missing_cols:
            raise ValueError(f"Value columns not found in period '{period_key}': {missing_cols}")
```

- [ ] **Step 2: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: add data validation function"
```

---

## Task 4: 修正 fill_missing_values 逻辑

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py:79-96`

- [ ] **Step 1: 修改 fill_missing_values 函数**

将 L79-96 替换为:

```python
def fill_missing_values(df: pd.DataFrame, key_column: str, value_columns: list) -> pd.DataFrame:
    """
    Fill missing values for existing points.
    
    Logic:
    - Point exists in both periods but data missing → fill with 0
    - Point only exists in one period → keep NaN (comparison shows N/A)
    """
    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        current_col = f"{col_name}_current"
        previous_col = f"{col_name}_previous"
        
        if current_col in df.columns and previous_col in df.columns:
            both_have_data = df[current_col].notna() & df[previous_col].notna()
            one_has_data = df[current_col].notna() | df[previous_col].notna()
            fill_mask = one_has_data & ~both_have_data
            
            df.loc[fill_mask, current_col] = df.loc[fill_mask, current_col].fillna(0)
            df.loc[fill_mask, previous_col] = df.loc[fill_mask, previous_col].fillna(0)
    
    return df
```

- [ ] **Step 2: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: correct fill_missing_values logic to match docstring"
```

---

## Task 5: 修复空字符串列名处理

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py:146-163`

- [ ] **Step 1: 修改 reorder_value_columns 函数**

将 L146-163 替换为:

```python
def reorder_value_columns(value_columns: list) -> list:
    """
    Reorder columns: priority columns (含'总') first, then others.
    """
    priority = []
    others = []
    
    for vc in value_columns:
        col_name = vc['name'] if isinstance(vc, dict) else vc
        if not col_name:
            continue
        first_char = col_name[0]
        is_priority = (first_char == '总')
        
        if is_priority:
            priority.append(vc)
        else:
            others.append(vc)
    
    return priority + others
```

- [ ] **Step 2: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: handle empty column name in reorder_value_columns"
```

---

## Task 6: 修复 generate_group_summary 边界检查

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py:190-252`

- [ ] **Step 1: 在 generate_group_summary 开头添加验证**

在 L205 (group_col = group_config['column']) 后添加:

```python
    current_df = data[periods['current']].copy()
    previous_df = data[periods['previous']].copy()
    
    if group_col not in current_df.columns:
        raise ValueError(f"Group column '{group_col}' not found in current period data")
    if group_col not in previous_df.columns:
        raise ValueError(f"Group column '{group_col}' not found in previous period data")
```

- [ ] **Step 2: 在过滤后添加空检查**

在 L213-214 (null_handling 过滤) 后添加:

```python
    if null_handling == 'ignore':
        current_df = current_df[current_df[group_col].notna()]
        previous_df = previous_df[previous_df[group_col].notna()]
    
    if current_df.empty:
        raise ValueError("Current period data is empty after filtering null group values")
    if previous_df.empty:
        raise ValueError("Previous period data is empty after filtering null group values")
```

- [ ] **Step 3: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 4: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: add boundary checks in generate_group_summary"
```

---

## Task 7: 修改 generate_report 主函数集成验证

**Files:**
- Modify: `.opencode/skills/data-analysis-report/scripts/generate_report.py:388-489`

- [ ] **Step 1: 在 generate_report 开头添加配置验证**

在 L398 (config = load_config(config_path)) 后添加:

```python
    config = load_config(config_path)
    validate_config(config)
```

- [ ] **Step 2: 在 load_data 后添加数据验证**

在 L400 (data = load_data(config)) 后添加:

```python
    data = load_data(config)
    validate_data(data, config['periods'], config['key_column'], config['value_columns'])
```

- [ ] **Step 3: 使用 sanitize_filename 处理输出文件名**

将 L479-480 替换为:

```python
    time_str = datetime.now().strftime('%H%M%S')
    safe_title = sanitize_filename(config['output']['title'])
    output_file = output_dir / f"{safe_title}_{time_str}.xlsx"
```

- [ ] **Step 4: 验证语法正确**

Run: `.venv\Scripts\python.exe -m py_compile .opencode/skills/data-analysis-report/scripts/generate_report.py`
Expected: No output (success)

- [ ] **Step 5: Commit**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: integrate validation functions in generate_report main flow"
```

---

## Task 8: 运行完整测试验证

**Files:**
- Test with existing config

- [ ] **Step 1: 查找现有测试配置**

Run: `Get-ChildItem -Recurse -Include "*.yaml" | Select-Object -First 5`
Expected: List of YAML config files

- [ ] **Step 2: 运行脚本验证修复**

Run: `.venv\Scripts\python.exe .opencode/skills/data-analysis-report/scripts/generate_report.py data/config.yaml`
Expected: 报表已生成 或 配置验证错误

- [ ] **Step 3: 最终提交**

```bash
git add .opencode/skills/data-analysis-report/scripts/generate_report.py
git commit -m "fix: complete security and quality fixes for generate_report.py"
```

---

## 修复总结

| 问题类型 | 修复任务 | 风险等级 |
|----------|----------|----------|
| 路径注入 | Task 1, Task 7 | 中等 |
| 空数据集 | Task 3, Task 6 | 高 |
| 列名不存在 | Task 3 | 高 |
| fill_missing_values 逻辑 | Task 4 | 高 |
| 空字符串列名 | Task 5 | 中等 |
| 配置缺失 | Task 2, Task 7 | 中等 |
| group_by 边界 | Task 6 | 中等 |
