# 兼职运维数据集成设计

## 背景

当前系统仅分析销售数据，需要扩展支持兼职运维记录，统计每个点位的运维频次。

## 目标

1. 加载兼职运维 Excel 文件
2. 通过机器码匹配点位
3. 统计每个点位的运维次数
4. 将运维次数作为新列添加到分析表
5. 未匹配的运维记录输出到独立分页

## 数据格式

### 运维记录（督导表.xlsx）

- `站点名称` 字段格式：`线路/机器码/点位名称/运维人员` 或 `线路/点位名称/机器码`
- 机器码为 5 位数字，如 `23398`, `12267`
- `提交时间` 字段记录运维时间

### 销售汇总表

- `机器编号` 列为 5 位整数
- `点位名称` 列为点位名称

## 匹配策略

**机器码精确匹配：**
1. 从运维记录的 `站点名称` 中提取 5 位机器码
2. 与销售表的 `机器编号` 精确匹配
3. 匹配成功 → 关联到对应点位
4. 匹配失败 → 输出到"待确认运维"分页

## 架构设计

### 新增模块

#### `src/data_analysis/matcher.py` - 点位匹配器

```python
def extract_machine_code(site_name: str) -> str | None:
    """从站点名称提取 5 位机器码"""

def match_by_machine_code(maintenance_df, sales_df, code_col, name_col) -> dict:
    """机器码匹配，返回 {机器编号: 点位名称} 映射"""

def get_unmatched_records(maintenance_df, matched_codes: set) -> DataFrame:
    """获取未匹配的运维记录"""
```

#### `src/data_analysis/maintenance.py` - 运维数据处理

```python
def load_maintenance_data(file_path: str) -> DataFrame:
    """加载运维 Excel"""

def count_maintenance_by_point(maintenance_df, point_mapping: dict, 
                                site_col: str) -> dict:
    """按点位统计运维次数"""

def generate_unmatched_sheet(unmatched_df, site_col: str) -> DataFrame:
    """生成待确认运维分页数据"""
```

### 修改模块

#### `analyzer.py`

新增函数：
```python
def merge_maintenance_counts(df: DataFrame, maintenance_counts: dict, 
                             key_column: str) -> DataFrame:
    """将运维次数合并到分析表"""
```

#### `report.py`

修改 `generate_report()`:
- 接收 `maintenance_file` 参数
- 调用匹配和统计逻辑
- 在输出 DataFrame 中增加"运维次数"列
- 生成"待确认运维"分页

#### `__init__.py`

导出新模块函数。

#### `run_analysis.py`

新增 CLI 参数：
```
--maintenance FILE   兼职运维表路径（可选）
```

## 配置扩展

`config.yaml` 新增：
```yaml
maintenance:
  file: ./misc/督导表.xlsx  # 可选
  site_column: 站点名称
  time_column: 提交时间
```

## 输出变化

### 分析表新增列

| 点位名称 | ... | 运维次数 |
|---------|-----|---------|
| 江门戴爱莲 | ... | 2 |

### 新增分页

**待确认运维** - 包含未匹配的运维记录原始数据，供人工处理。

## 开发计划

1. 创建 git 分支 `feature/maintenance-integration`
2. 实现 `matcher.py`
3. 实现 `maintenance.py`
4. 修改 `analyzer.py`
5. 修改 `report.py`
6. 更新 `__init__.py`
7. 更新 `run_analysis.py`
8. 测试验证
9. 合并到主分支

## 风险与应对

| 风险 | 应对 |
|-----|-----|
| 机器码格式变化 | 正则表达式容错处理 |
| 运维表字段名变化 | 配置化字段名 |
| 大数据量性能 | 批量处理，避免逐行循环 |
