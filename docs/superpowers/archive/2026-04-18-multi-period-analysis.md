# 多周期数据分析报表实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展 run_analysis.py 支持年度、季度、月度、自定义时间范围四种周期类型

**Architecture:** 新增 PeriodParser 模块处理周期识别，FileValidator 模块验证数据文件存在性，修改主脚本集成这些模块

**Tech Stack:** Python 3.x, argparse, re, pathlib

---

## 文件结构

| 文件 | 操作 | 说明 |
|------|------|------|
| `scripts/period_parser.py` | 新建 | 周期类型识别器 |
| `scripts/run_analysis.py` | 修改 | 集成周期识别和文件验证 |
| `Makefile` | 修改 | 更新帮助信息和示例 |

---

### Task 1: 创建周期识别器 PeriodParser

**Files:**
- Create: `scripts/period_parser.py`

- [ ] **Step 1: 创建 period_parser.py 基础结构**

```python
#!/usr/bin/env python3
"""
周期类型识别器

支持的格式:
- 年度: 2026
- 季度: 2026Q1
- 月度: 2026.03
- 自定义: 2026.04.13~2026.04.19
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PeriodType(Enum):
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"
    CUSTOM = "custom"


@dataclass
class PeriodInfo:
    period_type: PeriodType
    raw_input: str
    file_name: str
    label: str
    short_label: Optional[str] = None


class PeriodParser:
    """周期类型识别器"""
    
    FILE_PREFIX = "销售汇总表-"
    
    @classmethod
    def parse(cls, period_str: str, force_type: Optional[str] = None) -> PeriodInfo:
        """
        解析周期字符串
        
        Args:
            period_str: 周期字符串 (如: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19)
            force_type: 强制指定类型 (year/quarter/month/custom)
        
        Returns:
            PeriodInfo 对象
        
        Raises:
            ValueError: 无法识别格式时抛出
        """
        if force_type:
            return cls._parse_by_type(period_str, force_type)
        return cls._auto_detect(period_str)
    
    @classmethod
    def _parse_by_type(cls, period_str: str, force_type: str) -> PeriodInfo:
        """按指定类型解析"""
        type_map = {
            "year": PeriodType.YEAR,
            "quarter": PeriodType.QUARTER,
            "month": PeriodType.MONTH,
            "custom": PeriodType.CUSTOM,
        }
        
        if force_type not in type_map:
            raise ValueError(f"不支持的类型: {force_type}。支持的类型: year, quarter, month, custom")
        
        period_type = type_map[force_type]
        return cls._build_period_info(period_str, period_type)
    
    @classmethod
    def _auto_detect(cls, period_str: str) -> PeriodInfo:
        """自动识别周期类型"""
        if "~" in period_str:
            return cls._build_period_info(period_str, PeriodType.CUSTOM)
        
        if re.match(r"^\d{4}Q[1-4]$", period_str):
            return cls._build_period_info(period_str, PeriodType.QUARTER)
        
        if re.match(r"^\d{4}\.\d{2}$", period_str):
            return cls._build_period_info(period_str, PeriodType.MONTH)
        
        if re.match(r"^\d{4}$", period_str):
            return cls._build_period_info(period_str, PeriodType.YEAR)
        
        raise ValueError(
            f"无法识别周期格式 '{period_str}'。"
            f"支持的格式: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19"
        )
    
    @classmethod
    def _build_period_info(cls, period_str: str, period_type: PeriodType) -> PeriodInfo:
        """构建 PeriodInfo 对象"""
        file_name = f"{cls.FILE_PREFIX}{period_str}.xlsx"
        short_label = None
        
        if period_type == PeriodType.CUSTOM:
            short_label = cls._extract_short_label(period_str)
        
        return PeriodInfo(
            period_type=period_type,
            raw_input=period_str,
            file_name=file_name,
            label=period_str,
            short_label=short_label
        )
    
    @classmethod
    def _extract_short_label(cls, period_str: str) -> str:
        """
        从自定义范围提取简短标签
        
        输入: 2026.04.13~2026.04.19
        输出: 04.13~04.19
        """
        match = re.match(r"^\d{4}\.(\d{2}\.\d{2})~\d{4}\.(\d{2}\.\d{2})$", period_str)
        if match:
            return f"{match.group(1)}~{match.group(2)}"
        return period_str
    
    @classmethod
    def generate_title(cls, current: PeriodInfo, previous: PeriodInfo) -> str:
        """
        生成报表标题
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            报表标题字符串
        """
        type_labels = {
            PeriodType.YEAR: "年度",
            PeriodType.QUARTER: "季度",
            PeriodType.MONTH: "月度",
        }
        
        if current.period_type == PeriodType.CUSTOM:
            curr_short = current.short_label or current.label
            prev_short = previous.short_label or previous.label
            return f"{prev_short}与{curr_short}销售分析"
        
        type_label = type_labels.get(current.period_type, "")
        return f"{previous.label}-{current.label}{type_label}销售分析"
```

- [ ] **Step 2: 验证 period_parser.py 语法正确**

Run: `.venv\Scripts\python.exe -m py_compile scripts/period_parser.py`
Expected: 无输出表示成功

- [ ] **Step 3: 提交 PeriodParser 模块**

```bash
git add scripts/period_parser.py
git commit -m "feat: add PeriodParser for multi-period type detection"
```

---

### Task 2: 创建文件验证器 FileValidator

**Files:**
- Create: `scripts/file_validator.py`

- [ ] **Step 1: 创建 file_validator.py**

```python
#!/usr/bin/env python3
"""
文件验证器 - 检查数据文件是否存在
"""

from pathlib import Path
from typing import List, Tuple

from period_parser import PeriodInfo


class FileValidator:
    """数据文件验证器"""
    
    DATA_DIR = Path("data")
    
    @classmethod
    def validate(cls, current: PeriodInfo, previous: PeriodInfo) -> Tuple[bool, List[str]]:
        """
        验证数据文件是否存在
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            (是否全部存在, 错误信息列表)
        """
        errors = []
        
        current_path = cls.DATA_DIR / current.file_name
        previous_path = cls.DATA_DIR / previous.file_name
        
        if not current_path.exists():
            errors.append(f"错误: 未找到当前期数据文件: data/{current.file_name}")
        
        if not previous_path.exists():
            errors.append(f"错误: 未找到对比期数据文件: data/{previous.file_name}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_file_paths(cls, current: PeriodInfo, previous: PeriodInfo) -> Tuple[Path, Path]:
        """
        获取数据文件完整路径
        
        Args:
            current: 当前期信息
            previous: 对比期信息
        
        Returns:
            (当前期路径, 对比期路径)
        """
        return (
            cls.DATA_DIR / current.file_name,
            cls.DATA_DIR / previous.file_name
        )
```

- [ ] **Step 2: 验证 file_validator.py 语法正确**

Run: `.venv\Scripts\python.exe -m py_compile scripts/file_validator.py`
Expected: 无输出表示成功

- [ ] **Step 3: 提交 FileValidator 模块**

```bash
git add scripts/file_validator.py
git commit -m "feat: add FileValidator for data file existence check"
```

---

### Task 3: 修改 run_analysis.py 集成新模块

**Files:**
- Modify: `scripts/run_analysis.py`

- [ ] **Step 1: 更新导入部分 (第1-36行)**

将第1-36行替换为:

```python
#!/usr/bin/env python3
"""
独立数据分析脚本 - 支持多种周期类型

用法:
    python scripts/run_analysis.py --current 2026 --previous 2025
    python scripts/run_analysis.py -c 2026Q1 -p 2025Q1
    python scripts/run_analysis.py -c 2026.03 -p 2026.02
    python scripts/run_analysis.py -c 2026.04.13~2026.04.19 -p 2026.04.06~2026.04.12
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from period_parser import PeriodParser, PeriodInfo
from file_validator import FileValidator

sys.path.insert(0, str(Path(__file__).parent.parent / '.opencode' / 'skills' / 'data-analysis-report' / 'scripts'))

from generate_report import (
    load_data, validate_data, merge_periods, fill_missing_values,
    calculate_analysis, add_totals, reorder_value_columns,
    generate_group_summary, filter_group_metrics,
    style_workbook, style_group_sheet, sanitize_filename
)
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

DEFAULT_VALUE_COLUMNS = [
    '总杯数', '总金额', '线上杯数', '线下杯数', '线上金额', '线下金额', '测试杯'
]

DEFAULT_GROUP_COLUMN = '督导人员'
```

- [ ] **Step 2: 更新 create_config 函数 (第39-75行)**

将第39-75行替换为:

```python
def create_config(args, current_info: PeriodInfo, previous_info: PeriodInfo):
    """根据命令行参数创建配置"""
    current_path, previous_path = FileValidator.get_file_paths(current_info, previous_info)
    
    config = {
        'data_source': {
            'type': 'multi_file',
            'files': [
                str(current_path),
                str(previous_path)
            ]
        },
        'key_column': '点位名称',
        'value_columns': [{'name': col} for col in args.columns],
        'periods': {
            'current': current_info.label,
            'previous': previous_info.label,
            'current_file': current_info.file_name.replace('.xlsx', ''),
            'previous_file': previous_info.file_name.replace('.xlsx', '')
        },
        'analysis': ['yoy'],
        'output': {
            'dir': './output',
            'title': args.title or PeriodParser.generate_title(current_info, previous_info)
        }
    }
    
    if args.group:
        config['group_by'] = {
            'column': args.group,
            'sheet_name': f'{args.group}汇总',
            'metrics': 'auto',
            'null_handling': 'ignore'
        }
    
    return config
```

- [ ] **Step 3: 更新 main 函数 (第155-192行)**

将第155-192行替换为:

```python
def main():
    parser = argparse.ArgumentParser(
        description='生成销售数据分析报表 (支持年度/季度/月度/自定义时间范围)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 年度分析
  %(prog)s -c 2026 -p 2025
  
  # 季度分析
  %(prog)s -c 2026Q1 -p 2025Q1
  
  # 月度分析
  %(prog)s -c 2026.03 -p 2026.02
  
  # 自定义时间范围
  %(prog)s -c 2026.04.13~2026.04.19 -p 2026.04.06~2026.04.12
  
  # 强制指定类型
  %(prog)s -c 2026.03 -p 2026.02 --type quarter
  
  # 其他参数
  %(prog)s -c 2026.03 -p 2026.02 --group 督导人员
  %(prog)s -c 2026.03 -p 2026.02 --columns 总杯数 总金额
        '''
    )
    
    parser.add_argument('-c', '--current', required=True,
                        help='当前期 (如: 2026, 2026Q1, 2026.03, 2026.04.13~2026.04.19)')
    parser.add_argument('-p', '--previous', required=True,
                        help='对比期 (如: 2025, 2025Q1, 2026.02, 2026.04.06~2026.04.12)')
    parser.add_argument('--type', dest='period_type', choices=['year', 'quarter', 'month', 'custom'],
                        help='强制指定周期类型 (默认自动识别)')
    parser.add_argument('-g', '--group', default=DEFAULT_GROUP_COLUMN,
                        help=f'分组列 (默认: {DEFAULT_GROUP_COLUMN})')
    parser.add_argument('--columns', nargs='+', default=DEFAULT_VALUE_COLUMNS,
                        help=f'分析列 (默认: {DEFAULT_VALUE_COLUMNS})')
    parser.add_argument('-t', '--title', help='报表标题')
    
    args = parser.parse_args()
    
    try:
        current_info = PeriodParser.parse(args.current, args.period_type)
        previous_info = PeriodParser.parse(args.previous, args.period_type)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    
    valid, errors = FileValidator.validate(current_info, previous_info)
    if not valid:
        for error in errors:
            print(error)
        sys.exit(1)
    
    print(f"数据源: {current_info.file_name}, {previous_info.file_name}")
    
    config = create_config(args, current_info, previous_info)
    
    print(f"正在生成报表: {previous_info.label} vs {current_info.label}")
    
    output_file, point_count, group_count = generate_report_from_config(config)
    
    print(f"报表已生成: {output_file}")
    print(f"点位数量: {point_count}")
    if group_count > 0:
        print(f"分组汇总: {group_count} 条")


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 验证脚本语法正确**

Run: `.venv\Scripts\python.exe -m py_compile scripts/run_analysis.py`
Expected: 无输出表示成功

- [ ] **Step 5: 测试月度格式 (向后兼容)**

Run: `.venv\Scripts\python.exe scripts/run_analysis.py -c 2026.03 -p 2026.02`
Expected: 成功生成报表

- [ ] **Step 6: 测试错误处理 - 无效格式**

Run: `.venv\Scripts\python.exe scripts/run_analysis.py -c abc -p def`
Expected: 显示支持的格式列表

- [ ] **Step 7: 测试错误处理 - 文件不存在**

Run: `.venv\Scripts\python.exe scripts/run_analysis.py -c 2026 -p 2025`
Expected: 显示未找到数据文件错误

- [ ] **Step 8: 提交 run_analysis.py 更新**

```bash
git add scripts/run_analysis.py
git commit -m "feat: integrate PeriodParser and FileValidator into run_analysis.py"
```

---

### Task 4: 更新 Makefile

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: 更新 Makefile**

将整个文件替换为:

```makefile
.PHONY: analyze clean help

help:
	@echo Available commands:
	@echo   make analyze c=2026 p=2025                    # Yearly
	@echo   make analyze c=2026Q1 p=2025Q1                # Quarterly
	@echo   make analyze c=2026.03 p=2026.02              # Monthly
	@echo   make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12  # Custom range
	@echo   make clean                                    # Clean output
	@echo   make help                                     # Show this help

analyze:
	@.venv\Scripts\python.exe scripts/run_analysis.py --current $(c) --previous $(p) $(if $(type),--type $(type)) $(if $(group),--group $(group)) $(if $(columns),--columns $(columns)) $(if $(title),--title $(title))

clean:
	@.venv\Scripts\python.exe scripts/cleanup.py
```

- [ ] **Step 2: 测试 Makefile 帮助**

Run: `make help`
Expected: 显示更新后的帮助信息

- [ ] **Step 3: 测试月度分析**

Run: `make analyze c=2026.03 p=2026.02`
Expected: 成功生成报表

- [ ] **Step 4: 提交 Makefile 更新**

```bash
git add Makefile
git commit -m "docs: update Makefile with multi-period examples"
```

---

### Task 5: 更新 AGENTS.md 文档

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: 更新 AGENTS.md 命令部分**

将第3-8行替换为:

```markdown
## Commands
- Run analysis: `make analyze c=PERIOD p=PERIOD`
  - Yearly: `make analyze c=2026 p=2025`
  - Quarterly: `make analyze c=2026Q1 p=2025Q1`
  - Monthly: `make analyze c=2026.03 p=2026.02`
  - Custom: `make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12`
- Install deps: `.venv\Scripts\pip install -r requirements.txt`
- Activate venv: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
- Clean up: `make clean` or `.venv\Scripts\python.exe scripts\cleanup.py`
- Help: `make help`
```

- [ ] **Step 2: 提交文档更新**

```bash
git add AGENTS.md
git commit -m "docs: update AGENTS.md with multi-period commands"
```

---

## 验收清单

- [ ] 年度格式 `2026` 正确识别并生成文件名
- [ ] 季度格式 `2026Q1` 正确识别并生成文件名
- [ ] 月度格式 `2026.03` 正确识别并生成文件名
- [ ] 自定义格式 `2026.04.13~2026.04.19` 正确识别并生成文件名
- [ ] 无效格式显示支持的格式列表
- [ ] 文件不存在时显示明确错误信息
- [ ] 报表标题按周期类型正确生成
- [ ] 向后兼容：现有月度命令继续正常工作
