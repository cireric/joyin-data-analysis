# Data Analysis Project

## Commands
- Run analysis: `make analyze c=PERIOD p=PERIOD`
  - Yearly: `make analyze c=2026 p=2025`
  - Quarterly: `make analyze c=2026Q1 p=2025Q1`
  - Monthly: `make analyze c=2026.03 p=2026.02`
  - Custom: `make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12`
- PDF to Word: `python scripts/pdf2word.py input.pdf [-o output.docx] [--pages 1-5] [--mode strict] [--debug]`
- Install deps: `.venv\Scripts\pip install -r requirements.txt`
- Activate venv: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
- Clean up: `make clean` or `.venv\Scripts\python.exe scripts\cleanup.py`
- Help: `make help`

## Structure
- `data/` - Input Excel files
- `output/` - Generated analysis reports (auto-created)
- `scripts/` - Utility scripts (run_analysis.py, cleanup.py)
- Main entry: `scripts/run_analysis.py` - standalone script with CLI args
- Makefile: `make analyze c=YYYY.MM p=YYYY.MM`

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
