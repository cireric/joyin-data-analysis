# Data Analysis Project

## Commands
- Run analysis: `make analyze c=PERIOD p=PERIOD`
  - Yearly: `make analyze c=2026 p=2025`
  - Quarterly: `make analyze c=2026Q1 p=2025Q1`
  - Monthly: `make analyze c=2026.03 p=2026.02`
  - Custom: `make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12`
- PDF to Word: `python scripts/pdf2word.py input.pdf [-o output.docx] [--pages 1-5] [--preset contract] [--force] [--debug]`
- Markdown to Word: `python scripts/md2word.py input.md [-o output.docx] [--reference-docx template.docx] [--toc] [--force]`
- URL to Markdown: `python scripts/url2md.py <url> [--output dir/] [--download-images] [--limit N] [--delay N] [--resume]`
- Install deps: `.venv\Scripts\pip install -r requirements.txt`
- Activate venv: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
- Clean up: `make clean` or `.venv\Scripts\python.exe scripts\cleanup.py`
- Help: `make help`

## Structure
- `data/` - Input Excel files
- `output/` - Generated analysis reports (auto-created)
- `src/data_analysis/` - Core library modules
  - `loader.py` - Data loading and validation
  - `analyzer.py` - Data analysis functions
  - `report.py` - Report generation
  - `styler.py` - Excel styling
- `scripts/` - CLI entry points
  - `run_analysis.py` - Main analysis script
  - `pdf2word.py` - PDF to Word converter
  - `md2word.py` - Markdown to Word converter
  - `cleanup.py` - Output cleanup
- `tests/` - Unit tests
- Makefile: `make analyze c=YYYY.MM p=YYYY.MM`

## Dependencies
- pandas, numpy, openpyxl, pdf2docx, pypandoc (see requirements.txt)
- Virtual environment: `.venv/` (create with `python -m venv .venv` if missing)

## Code Style
- All files must use UTF-8 encoding
- After editing any file (code or markdown), always format it:
  - Remove trailing whitespace
  - Ensure consistent indentation
  - Remove extra blank lines

## MCP Tools
- When you need to search documentation for any library (PHP, Python, JavaScript, etc.), use `context7` tools.
- When you need to search real-world code examples from GitHub, use `gh_grep` tools.
- When you need to capture, analyze, or interact with web pages, use `playwright` tools.
- When you need to analyze images, screenshots, UI designs, diagrams, charts, or videos, use `vision` tools (e.g. `vision_image_analysis`, `vision_extract_text_from_screenshot`, `vision_ui_to_artifact`, `vision_diagnose_error_screenshot`, etc.).

## Security Rules
- All file operations (read, write, edit) must be restricted to the project directory (`D:\Project\source\__TEST__\data_analysis\`) — accessing or modifying files outside this path is prohibited.
- **CRITICAL**: Any operations on files or directories outside the project directory (including read, write, delete, and all other operations) MUST receive explicit user confirmation before proceeding.

## Workflow
- After writing code, verify by running the script and checking output
- Design documents should be placed in `docs/superpowers/specs/`
- Implementation plans should be placed in `docs/superpowers/plans/`
- Completed implementation plans should be archived to `docs/superpowers/archive/` after user confirmation
