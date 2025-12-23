# Use shell to find Python at runtime (checks conda, venv, then system)
PYTHON_CMD = $(shell if [ -n "$$CONDA_PREFIX" ]; then echo "$$CONDA_PREFIX/bin/python"; elif [ -n "$$VIRTUAL_ENV" ]; then echo "$$VIRTUAL_ENV/bin/python"; elif command -v python3 >/dev/null 2>&1; then command -v python3; elif command -v python >/dev/null 2>&1; then command -v python; else echo "python3"; fi)

.PHONY: help format format-js format-py lint lint-js lint-py test test-unit test-e2e check-all install-dev-deps install-python-deps

help: ## Show this help message
	@echo "WaveWatch Development Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install-dev-deps: install-python-deps ## Install all development dependencies
	@echo "📦 Installing JavaScript dev dependencies..."
	@cd src/wavewatch/ui/client && npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-react eslint-plugin-react-hooks
	@echo "✅ All dev dependencies installed"

install-python-deps: ## Install Python development dependencies (Black, Flake8)
	@echo "📦 Installing Python dev dependencies..."
	@pip install -r requirements-dev.txt
	@echo "✅ Python dev dependencies installed"

format: format-js format-py ## Format all code (JavaScript and Python)

format-js: ## Format JavaScript/JSX code with Prettier
	@echo "🎨 Formatting JavaScript/JSX files..."
	@npx prettier --write 'src/**/*.{js,jsx,json,md}' || (echo "⚠️  Prettier not found. Run 'make install-dev-deps' first" && exit 1)

format-py: ## Format Python code with Black
	@echo "🎨 Formatting Python files..."
	@bash -c 'if command -v conda >/dev/null 2>&1 && conda env list | grep -q "wavewatch"; then conda run -n wavewatch python -m black src/wavewatch/ surf_api.py; elif [ -n "$$CONDA_PREFIX" ]; then "$$CONDA_PREFIX/bin/python" -m black src/wavewatch/ surf_api.py; elif [ -n "$$VIRTUAL_ENV" ]; then "$$VIRTUAL_ENV/bin/python" -m black src/wavewatch/ surf_api.py; elif command -v python3 >/dev/null 2>&1; then python3 -m black src/wavewatch/ surf_api.py; elif command -v python >/dev/null 2>&1; then python -m black src/wavewatch/ surf_api.py; else echo "⚠️  Python not found"; exit 1; fi' || (echo "⚠️  Black not found. Make sure your conda environment 'wavewatch' is activated and install dev dependencies with: pip install -r requirements-dev.txt" && exit 1)

lint: lint-js lint-py ## Lint all code (JavaScript and Python)

lint-js: ## Lint JavaScript/JSX code with ESLint
	@echo "🔍 Linting JavaScript/JSX files..."
	@npx eslint 'src/**/*.{js,jsx}' || (echo "⚠️  ESLint not found. Run 'make install-dev-deps' first" && exit 1)

lint-py: ## Lint Python code with Flake8
	@echo "🔍 Linting Python files..."
	@bash -c 'if command -v conda >/dev/null 2>&1 && conda env list | grep -q "wavewatch"; then OUTPUT=$$(conda run -n wavewatch python -m flake8 src/wavewatch/ surf_api.py 2>&1); EXIT=$$?; echo "$$OUTPUT" | grep -v "ERROR conda.cli.main_run"; exit $$EXIT; elif [ -n "$$CONDA_PREFIX" ]; then "$$CONDA_PREFIX/bin/python" -m flake8 src/wavewatch/ surf_api.py; elif [ -n "$$VIRTUAL_ENV" ]; then "$$VIRTUAL_ENV/bin/python" -m flake8 src/wavewatch/ surf_api.py; elif command -v python3 >/dev/null 2>&1; then python3 -m flake8 src/wavewatch/ surf_api.py; elif command -v python >/dev/null 2>&1; then python -m flake8 src/wavewatch/ surf_api.py; else echo "⚠️  Python not found. Make sure your conda environment '\''wavewatch'\'' is activated."; exit 127; fi' || (EXIT_CODE=$$?; if [ $$EXIT_CODE -eq 127 ]; then echo "⚠️  Flake8 not found. Install dev dependencies with: pip install -r requirements-dev.txt"; exit 1; fi; exit $$EXIT_CODE)

test: test-unit test-e2e ## Run all tests

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	@echo "⚠️  Tests are currently disabled (no tests found)"
	@# @cd src/wavewatch/ui/client && npm test -- --watchAll=false --passWithNoTests

test-e2e: ## Run E2E tests (not yet configured)
	@echo "🧪 E2E tests not yet configured"

check-all: lint ## Run all linting and tests (use before committing)
	@echo "✅ All checks passed!"
	@# Note: Tests are commented out until test files are added

