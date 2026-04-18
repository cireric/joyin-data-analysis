# Data Analysis Project

## Commands
- Run analysis: `.venv\Scripts\python.exe data_analysis_202603.py`
- Install deps: `.venv\Scripts\pip install -r requirements.txt`
- Activate venv: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
- Clean up: `.venv\Scripts\python.exe scripts\cleanup.py --dry-run` (preview) or `.venv\Scripts\python.exe scripts\cleanup.py` (execute)

## Structure
- `data/` - Input Excel files
- `output/` - Generated analysis reports (auto-created)
- `scripts/` - Utility scripts (cleanup, etc.)
- Main entry: `data_analysis_202603.py` - reads multi-sheet Excel and generates styled reports with 环比/同比 analysis

## Dependencies
- pandas, numpy, openpyxl (see requirements.txt)
- Virtual environment: `.venv/` (create with `python -m venv .venv` if missing)

## Skills
- `data-analysis-report` - Generate styled Excel analysis reports from multi-period data
  - Trigger: "分析数据", "生成报表", "同比分析", "汇总统计"
  - Supports: multi-sheet/multi-file Excel, YoY/MoM comparison
  - Location: `.opencode/skills/data-analysis-report/`

## Code Style
- All files must use UTF-8 encoding
- After editing any file (code or markdown), always format it:
  - Remove trailing whitespace
  - Ensure consistent indentation
  - Remove extra blank lines

## Workflow
- After writing code, verify by running the script and checking output
- Completed implementation plans should be archived to `docs/superpowers/archive/`
