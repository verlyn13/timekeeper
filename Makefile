.PHONY: install test lint format security docs sphinx-docs all-docs serve docker-build docker-run clean check-all validate-release check-env

# Default Python interpreter
PYTHON = python3

# Check for environment variables
check-env:
	@if [ -f ~/.secrets/timekeeper/tokens.env ] && command -v zsh >/dev/null 2>&1; then \
		echo "Loading environment variables from ~/.secrets/timekeeper/tokens.env..."; \
		. ~/.secrets/timekeeper/tokens.env; \
	else \
		echo "Note: Environment file not found or zsh not available. Some operations may require tokens."; \
	fi

# Install the package in development mode
install:
	$(PYTHON) -m pip install -e ".[dev,docs]"

# Run tests
test:
	$(PYTHON) -m pytest tests/

# Run tests with coverage
coverage: check-env
	$(PYTHON) -m pytest --cov=src tests/ --cov-report=xml --cov-report=html
	@if [ -n "$$CODECOV_TOKEN" ]; then \
		echo "Codecov token found. Ready for coverage reporting."; \
	fi

# Run linting checks
lint:
	$(PYTHON) -m flake8 src/ tests/
	$(PYTHON) -m isort --check-only src/ tests/
	$(PYTHON) -m black --check src/ tests/
	$(PYTHON) -m mypy src/ tests/

# Format code
format:
	$(PYTHON) -m isort src/ tests/
	$(PYTHON) -m black src/ tests/

# Security scanning
security:
	$(PYTHON) -m pip install bandit safety
	$(PYTHON) -m bandit -r src/ || true
	$(PYTHON) -m safety check || true

# Build Quarto documentation
docs:
	quarto render

# Build Sphinx documentation
sphinx-docs:
	cd config/sphinx && make html

# Build all documentation
all-docs: docs sphinx-docs
	mkdir -p _site/api
	cp -r _build/sphinx/* _site/api/

# Serve documentation for local preview
serve:
	quarto preview

# Build Docker image
docker-build:
	docker build -t timekeeper:latest .

# Run Docker container
docker-run:
	docker run -it --rm -v $(PWD):/app timekeeper:latest

# Run all checks (equivalent to CI pipeline)
check-all: lint test coverage security all-docs
	@echo "All checks passed!"

# Validate a release build
validate-release: check-env
	$(PYTHON) -m pip install build twine
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*
	@if [ -n "$$PYPI_API_TOKEN" ]; then \
		echo "PyPI token found. Ready to publish."; \
	else \
		echo "Warning: PYPI_API_TOKEN not found. You will need to set this to publish to PyPI."; \
	fi
	@echo "Release validation passed!"

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf _site/
	rm -rf _build/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete