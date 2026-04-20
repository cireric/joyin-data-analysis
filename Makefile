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
