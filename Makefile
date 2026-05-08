.PHONY: analyze clean crawl md2word md2pdf help

help:
	@echo Available commands:
	@echo   make analyze c=2026 p=2025                    # Yearly
	@echo   make analyze c=2026Q1 p=2025Q1                # Quarterly
	@echo   make analyze c=2026.03 p=2026.02              # Monthly
	@echo   make analyze c=2026.04.13~2026.04.19 p=2026.04.06~2026.04.12  # Custom range
	@echo   make crawl url=URL                            # URL to Markdown
	@echo   make crawl url=URL limit=10                   # Limit articles
	@echo   make crawl url=URL download=1                 # Download images
	@echo   make md2word input.md [ARGS]                  # Markdown to Word
	@echo   make md2pdf ARGS="--help"                     # Markdown to PDF
	@echo   make clean                                     # Clean output
	@echo   make help                                      # Show this help

analyze:
	@.venv\Scripts\python.exe scripts/run_analysis.py --current $(c) --previous $(p) $(if $(type),--type $(type)) $(if $(group),--group $(group)) $(if $(columns),--columns $(columns)) $(if $(title),--title $(title))

crawl:
	@.venv\Scripts\python.exe scripts/url2md.py "$(url)" $(if $(output),--output $(output)) $(if $(limit),--limit $(limit)) $(if $(delay),--delay $(delay)) $(if $(max_delay),--max-delay $(max_delay)) $(if $(download),--download-images) $(if $(resume),--resume) $(if $(state),--state $(state))

md2word:
	@.venv\Scripts\python.exe scripts/md2word.py $(filter-out $@,$(MAKECMDGOALS))

md2pdf:
	@.venv\Scripts\python.exe scripts/md2pdf.py $(ARGS)

clean:
	@.venv\Scripts\python.exe scripts/cleanup.py
