.PHONY: help setup install test examples clean format lint benchmark

help:
	@echo "BM25Comp Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup      - Create venv and install dependencies"
	@echo "  make install    - Install package in editable mode"
	@echo ""
	@echo "Development:"
	@echo "  make test       - Run all tests"
	@echo "  make examples   - Run all example scripts"
	@echo "  make benchmark  - Run quick benchmark"
	@echo "  make clean      - Remove build artifacts and caches"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format     - Format code (if black/ruff installed)"
	@echo "  make lint       - Lint code (if ruff installed)"

setup:
	@echo "Creating virtual environment with uv..."
	uv venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "Activate it with: source .venv/bin/activate"
	@echo "Then run: make install"

install:
	@echo "Installing package and dependencies..."
	uv pip install -e ".[dev]"
	@echo ""
	@echo "Installation complete!"
	@echo "Run 'make examples' to test it out."

test:
	@echo "Running tests..."
	pytest tests/ -v

examples:
	@echo "Running basic usage example..."
	@python examples/basic_usage.py
	@echo ""
	@echo "Running space efficiency example..."
	@python examples/space_efficiency.py
	@echo ""
	@echo "Running memory efficiency example..."
	@python examples/memory_efficiency.py
	@echo ""
	@echo "Running custom tokenization example..."
	@python examples/custom_tokenization.py

benchmark:
	@echo "Running quick benchmark with sample data..."
	@python benchmarks/run_benchmark.py benchmarks/data/sample.json

clean:
	@echo "Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.bm25" -delete
	@echo "Clean complete!"

format:
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Formatting with ruff..."; \
		ruff format src/ tests/ examples/; \
	elif command -v black >/dev/null 2>&1; then \
		echo "Formatting with black..."; \
		black src/ tests/ examples/; \
	else \
		echo "Install ruff or black for formatting: uv pip install ruff"; \
	fi

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		echo "Linting with ruff..."; \
		ruff check src/ tests/ examples/; \
	else \
		echo "Install ruff for linting: uv pip install ruff"; \
	fi
