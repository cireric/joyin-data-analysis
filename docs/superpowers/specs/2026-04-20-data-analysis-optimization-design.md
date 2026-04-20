# 数据分析程序最小可行优化设计

## 背景

数据分析程序存在以下问题：
1. 错误处理不一致：`period_parser.py` 抛异常，`file_validator.py` 返回元组
2. `generate_report_from_config()` 函数 75 行，职责过多

## 目标

最小可行优化：统一错误处理风格、拆分大函数，保持现有架构。

## 设计

### 1. 统一错误处理

**文件：** `scripts/file_validator.py`

**修改：** `validate()` 方法改为抛出异常

```python
# 修改前
@classmethod
def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> Tuple[bool, List[str]]:
    errors = []
    current_path = cls.DATA_DIR / current.file_name
    previous_path = cls.DATA_DIR / previous.file_name
    
    if not current_path.exists():
        errors.append(f"错误: 未找到当前期数据文件: data/{current.file_name}")
    if not previous_path.exists():
        errors.append(f"错误: 未找到对比期数据文件: data/{previous.file_name}")
    
    return len(errors) == 0, errors

# 修改后
@classmethod
def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> None:
    current_path = cls.DATA_DIR / current.file_name
    previous_path = cls.DATA_DIR / previous.file_name
    
    if not current_path.exists():
        raise FileNotFoundError(f"未找到当前期数据文件: data/{current.file_name}")
    if not previous_path.exists():
        raise FileNotFoundError(f"未找到对比期数据文件: data/{previous.file_name}")
```

**文件：** `scripts/run_analysis.py`

**修改：** 调用处改为 try/except

```python
# 修改前
valid, errors = FileValidator.validate(current_info, previous_info)
if not valid:
    for error in errors:
        print(error)
    sys.exit(1)

# 修改后
try:
    FileValidator.validate(current_info, previous_info)
except FileNotFoundError as e:
    print(f"错误: {e}")
    sys.exit(1)
```

### 2. 拆分大函数

**文件：** `scripts/run_analysis.py`

**修改：** 将 `generate_report_from_config()` 拆分为 3 个函数

```python
def load_and_validate(config: dict) -> dict:
    """加载数据并验证"""
    data = load_data(config)
    validate_data(data, config['periods'], config['key_column'], config['value_columns'])
    return data


def process_data(data: dict, config: dict) -> pd.DataFrame:
    """处理数据：合并、填充、计算、添加总计"""
    merged = merge_periods(data, config['periods'], config['key_column'], config['value_columns'])
    merged = fill_missing_values(merged, config['key_column'], config['value_columns'])
    result = calculate_analysis(merged, config['value_columns'], config['analysis'])
    result = add_totals(result, config['key_column'], config['value_columns'], config['analysis'])
    return result


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
        
        group_result = generate_group_summary(data, config['periods'], group_config, config['value_columns'], config['analysis'])
        
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


def generate_report_from_config(config: dict) -> tuple:
    """主函数：协调各步骤"""
    data = load_and_validate(config)
    result = process_data(data, config)
    return export_report(result, data, config)
```

## 影响范围

| 文件 | 修改类型 |
|------|----------|
| `scripts/file_validator.py` | 修改 `validate()` 返回类型 |
| `scripts/run_analysis.py` | 拆分函数 + 修改调用方式 |

## 验证

修改完成后运行：
```bash
make analyze c=2026.03 p=2026.02
```

确认报表正常生成。
