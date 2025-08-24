# MKD Automation - Comprehensive Development Makefile
# Provides automation for common development tasks

# Configuration
PYTHON := python3
PIP := pip3
PACKAGE_NAME := mkd-automation
SOURCE_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs
VENV_DIR := venv

# Virtual environment detection
ifdef VIRTUAL_ENV
    IN_VENV := true
else
    IN_VENV := false
endif

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m  
RED := \033[31m
BLUE := \033[34m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)MKD Automation - Development Tasks$(RESET)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*setup' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*dev' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*test' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quality Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*quality' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Documentation Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*docs' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Build & Deploy Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*build' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Utility Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+.*##.*util' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# =============================================================================
# Setup Commands
# =============================================================================

.PHONY: setup
setup: setup-venv install-dev ## setup: Complete development environment setup

.PHONY: setup-venv
setup-venv: ## setup: Create and activate virtual environment
	@echo "$(BLUE)Setting up virtual environment...$(RESET)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "$(GREEN)Virtual environment created at $(VENV_DIR)$(RESET)"; \
	else \
		echo "$(YELLOW)Virtual environment already exists$(RESET)"; \
	fi
	@echo "To activate: source $(VENV_DIR)/bin/activate"

.PHONY: install
install: ## setup: Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev: ## setup: Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

.PHONY: install-editable
install-editable: ## setup: Install package in editable mode
	@echo "$(BLUE)Installing package in editable mode...$(RESET)"
	$(PIP) install -e .

.PHONY: setup-pre-commit
setup-pre-commit: ## setup: Install and configure pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(RESET)"
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed$(RESET)"

# =============================================================================
# Development Commands
# =============================================================================

.PHONY: run
run: ## dev: Run the main application
	@echo "$(BLUE)Running MKD Automation...$(RESET)"
	$(PYTHON) $(SOURCE_DIR)/main.py

.PHONY: run-gui
run-gui: ## dev: Run the GUI application
	@echo "$(BLUE)Running MKD Automation GUI...$(RESET)"
	$(PYTHON) $(SOURCE_DIR)/main.py --gui

.PHONY: run-debug
run-debug: ## dev: Run with debug output
	@echo "$(BLUE)Running MKD Automation in debug mode...$(RESET)"
	$(PYTHON) $(SOURCE_DIR)/main.py --debug

.PHONY: shell
shell: ## dev: Start interactive Python shell with package loaded
	@echo "$(BLUE)Starting interactive shell...$(RESET)"
	$(PYTHON) -c "import sys; sys.path.insert(0, '$(SOURCE_DIR)'); import mkd; print('MKD package loaded'); import IPython; IPython.start_ipython()"

.PHONY: notebook
notebook: ## dev: Start Jupyter notebook server
	@echo "$(BLUE)Starting Jupyter notebook...$(RESET)"
	jupyter notebook --notebook-dir=.

# =============================================================================
# Testing Commands
# =============================================================================

.PHONY: test
test: ## test: Run all tests
	@echo "$(BLUE)Running all tests...$(RESET)"
	pytest

.PHONY: test-unit
test-unit: ## test: Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	pytest $(TESTS_DIR)/unit/ -v

.PHONY: test-integration
test-integration: ## test: Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	pytest $(TESTS_DIR)/integration/ -v

.PHONY: test-platform
test-platform: ## test: Run platform-specific tests
	@echo "$(BLUE)Running platform-specific tests...$(RESET)"
	pytest -m platform_specific -v

.PHONY: test-gui
test-gui: ## test: Run GUI tests (requires display)
	@echo "$(BLUE)Running GUI tests...$(RESET)"
	pytest -m gui -v

.PHONY: test-coverage
test-coverage: ## test: Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	pytest --cov=$(SOURCE_DIR)/mkd --cov-report=html --cov-report=term --cov-report=xml

.PHONY: test-fast
test-fast: ## test: Run tests excluding slow tests
	@echo "$(BLUE)Running fast tests...$(RESET)"
	pytest -m "not slow" --maxfail=5

.PHONY: test-parallel
test-parallel: ## test: Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(RESET)"
	pytest -n auto

.PHONY: test-watch
test-watch: ## test: Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	ptw -- --testmon

.PHONY: benchmark
benchmark: ## test: Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(RESET)"
	pytest --benchmark-only --benchmark-sort=mean

# =============================================================================
# Code Quality Commands
# =============================================================================

.PHONY: format
format: format-black format-isort ## quality: Format code with black and isort

.PHONY: format-black
format-black: ## quality: Format code with black
	@echo "$(BLUE)Formatting code with black...$(RESET)"
	black $(SOURCE_DIR) $(TESTS_DIR)

.PHONY: format-isort
format-isort: ## quality: Sort imports with isort
	@echo "$(BLUE)Sorting imports with isort...$(RESET)"
	isort $(SOURCE_DIR) $(TESTS_DIR)

.PHONY: format-check
format-check: ## quality: Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	black --check $(SOURCE_DIR) $(TESTS_DIR)
	isort --check $(SOURCE_DIR) $(TESTS_DIR)

.PHONY: lint
lint: lint-flake8 lint-pylint lint-mypy ## quality: Run all linters

.PHONY: lint-flake8
lint-flake8: ## quality: Run flake8 linter
	@echo "$(BLUE)Running flake8...$(RESET)"
	flake8 $(SOURCE_DIR) $(TESTS_DIR)

.PHONY: lint-pylint
lint-pylint: ## quality: Run pylint
	@echo "$(BLUE)Running pylint...$(RESET)"
	pylint $(SOURCE_DIR)

.PHONY: lint-mypy
lint-mypy: ## quality: Run mypy type checker
	@echo "$(BLUE)Running mypy...$(RESET)"
	mypy $(SOURCE_DIR)

.PHONY: security
security: security-bandit security-safety ## quality: Run security checks

.PHONY: security-bandit
security-bandit: ## quality: Run bandit security linter
	@echo "$(BLUE)Running bandit security check...$(RESET)"
	bandit -r $(SOURCE_DIR) -f json -o bandit-report.json || bandit -r $(SOURCE_DIR)

.PHONY: security-safety
security-safety: ## quality: Check dependencies for security vulnerabilities
	@echo "$(BLUE)Checking dependencies with safety...$(RESET)"
	safety check

.PHONY: quality-check
quality-check: format-check lint security ## quality: Run all quality checks

.PHONY: pre-commit-run
pre-commit-run: ## quality: Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	pre-commit run --all-files

# =============================================================================
# Documentation Commands
# =============================================================================

.PHONY: docs
docs: docs-build ## docs: Build documentation

.PHONY: docs-build
docs-build: ## docs: Build HTML documentation
	@echo "$(BLUE)Building documentation...$(RESET)"
	cd $(DOCS_DIR) && sphinx-build -b html . _build/html

.PHONY: docs-serve
docs-serve: docs-build ## docs: Build and serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(RESET)"
	cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8000

.PHONY: docs-clean
docs-clean: ## docs: Clean documentation build
	@echo "$(BLUE)Cleaning documentation build...$(RESET)"
	rm -rf $(DOCS_DIR)/_build

.PHONY: docs-linkcheck
docs-linkcheck: ## docs: Check documentation links
	@echo "$(BLUE)Checking documentation links...$(RESET)"
	cd $(DOCS_DIR) && sphinx-build -b linkcheck . _build/linkcheck

.PHONY: docs-auto
docs-auto: ## docs: Auto-build documentation on changes
	@echo "$(BLUE)Auto-building documentation...$(RESET)"
	sphinx-autobuild $(DOCS_DIR) $(DOCS_DIR)/_build/html --host 0.0.0.0

.PHONY: api-docs
api-docs: ## docs: Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(RESET)"
	sphinx-apidoc -o $(DOCS_DIR)/api $(SOURCE_DIR)/mkd --force

# =============================================================================
# Build & Deploy Commands
# =============================================================================

.PHONY: build
build: clean build-wheel build-sdist ## build: Build distribution packages

.PHONY: build-wheel
build-wheel: ## build: Build wheel distribution
	@echo "$(BLUE)Building wheel distribution...$(RESET)"
	$(PYTHON) -m build --wheel

.PHONY: build-sdist
build-sdist: ## build: Build source distribution
	@echo "$(BLUE)Building source distribution...$(RESET)"
	$(PYTHON) -m build --sdist

.PHONY: build-check
build-check: build ## build: Build and check distributions
	@echo "$(BLUE)Checking distributions...$(RESET)"
	twine check dist/*

.PHONY: upload-test
upload-test: build-check ## build: Upload to TestPyPI
	@echo "$(BLUE)Uploading to TestPyPI...$(RESET)"
	twine upload --repository testpypi dist/*

.PHONY: upload
upload: build-check ## build: Upload to PyPI
	@echo "$(YELLOW)Uploading to PyPI...$(RESET)"
	@echo "$(RED)Are you sure? This will publish to production PyPI.$(RESET)"
	@read -p "Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	twine upload dist/*

.PHONY: docker-build
docker-build: ## build: Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(PACKAGE_NAME):latest .

.PHONY: docker-run
docker-run: ## build: Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -it --rm $(PACKAGE_NAME):latest

# =============================================================================
# Environment Management
# =============================================================================

.PHONY: env-info
env-info: ## util: Show environment information
	@echo "$(BLUE)Environment Information:$(RESET)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Python executable: $$(which $(PYTHON))"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Virtual environment: $(IN_VENV)"
	@echo "Working directory: $$(pwd)"
	@echo "Git branch: $$(git branch --show-current 2>/dev/null || echo 'not a git repository')"
	@echo "Git status: $$(git status --porcelain 2>/dev/null | wc -l) files changed"

.PHONY: env-freeze
env-freeze: ## util: Generate requirements file from current environment
	@echo "$(BLUE)Generating requirements from current environment...$(RESET)"
	$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)Requirements saved to requirements-frozen.txt$(RESET)"

.PHONY: env-update
env-update: ## util: Update all dependencies to latest versions
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(PIP) install --upgrade -r requirements-dev.txt

.PHONY: env-check
env-check: ## util: Check environment and dependencies
	@echo "$(BLUE)Checking environment...$(RESET)"
	$(PIP) check
	@echo "$(GREEN)Environment check complete$(RESET)"

# =============================================================================
# Database & Data Management
# =============================================================================

.PHONY: db-init
db-init: ## util: Initialize database (if applicable)
	@echo "$(BLUE)Initializing database...$(RESET)"
	$(PYTHON) -c "from mkd.data import init_database; init_database()"

.PHONY: db-migrate
db-migrate: ## util: Run database migrations (if applicable)
	@echo "$(BLUE)Running database migrations...$(RESET)"
	$(PYTHON) -c "from mkd.data import migrate_database; migrate_database()"

.PHONY: sample-data
sample-data: ## util: Generate sample data for testing
	@echo "$(BLUE)Generating sample data...$(RESET)"
	$(PYTHON) -c "from tests.fixtures import generate_sample_data; generate_sample_data()"

# =============================================================================
# Performance & Profiling
# =============================================================================

.PHONY: profile
profile: ## util: Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(RESET)"
	$(PYTHON) -m cProfile -o profile_output.prof $(SOURCE_DIR)/main.py
	@echo "Profile saved to profile_output.prof"

.PHONY: profile-memory
profile-memory: ## util: Run memory profiling
	@echo "$(BLUE)Running memory profiling...$(RESET)"
	$(PYTHON) -m memory_profiler $(SOURCE_DIR)/main.py

.PHONY: profile-line
profile-line: ## util: Run line-by-line profiling
	@echo "$(BLUE)Running line profiling...$(RESET)"
	kernprof -l -v $(SOURCE_DIR)/main.py

# =============================================================================
# Git & Version Control
# =============================================================================

.PHONY: git-hooks
git-hooks: setup-pre-commit ## util: Setup git hooks

.PHONY: git-clean
git-clean: ## util: Clean git repository
	@echo "$(BLUE)Cleaning git repository...$(RESET)"
	git clean -fdx
	@echo "$(YELLOW)Warning: This removes all untracked files!$(RESET)"

.PHONY: version
version: ## util: Show current version
	@echo "$(BLUE)Current version:$(RESET)"
	@$(PYTHON) -c "from setuptools_scm import get_version; print(get_version())" 2>/dev/null || echo "Version not available (setuptools_scm required)"

.PHONY: tag
tag: ## util: Create new version tag
	@echo "$(BLUE)Current tags:$(RESET)"
	@git tag -l | tail -10
	@echo "$(BLUE)Enter new tag version:$(RESET)"
	@read -p "Version (e.g., v0.2.1): " version; \
	git tag -a "$$version" -m "Release $$version"; \
	echo "$(GREEN)Tag $$version created$(RESET)"

# =============================================================================
# Maintenance & Cleanup
# =============================================================================

.PHONY: clean
clean: clean-build clean-pyc clean-test clean-docs ## util: Clean all build artifacts

.PHONY: clean-build
clean-build: ## util: Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/

.PHONY: clean-pyc
clean-pyc: ## util: Clean Python cache files
	@echo "$(BLUE)Cleaning Python cache files...$(RESET)"
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete
	find . -name '__pycache__' -type d -exec rm -rf {} +
	find . -name '.pytest_cache' -type d -exec rm -rf {} +
	find . -name '.mypy_cache' -type d -exec rm -rf {} +

.PHONY: clean-test
clean-test: ## util: Clean test artifacts
	@echo "$(BLUE)Cleaning test artifacts...$(RESET)"
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf coverage.xml
	rm -rf *.prof

.PHONY: clean-docs
clean-docs: ## util: Clean documentation artifacts
	@echo "$(BLUE)Cleaning documentation artifacts...$(RESET)"
	rm -rf $(DOCS_DIR)/_build/

.PHONY: deep-clean
deep-clean: clean clean-venv ## util: Deep clean including virtual environment
	@echo "$(BLUE)Performing deep clean...$(RESET)"

.PHONY: clean-venv
clean-venv: ## util: Remove virtual environment
	@echo "$(BLUE)Removing virtual environment...$(RESET)"
	@if [ -d "$(VENV_DIR)" ]; then \
		rm -rf $(VENV_DIR); \
		echo "$(GREEN)Virtual environment removed$(RESET)"; \
	else \
		echo "$(YELLOW)No virtual environment found$(RESET)"; \
	fi

# =============================================================================
# Multi-platform Testing
# =============================================================================

.PHONY: test-all-platforms
test-all-platforms: ## test: Run tests across all supported Python versions
	@echo "$(BLUE)Running tests across all platforms...$(RESET)"
	tox

.PHONY: test-python39
test-python39: ## test: Run tests with Python 3.9
	@echo "$(BLUE)Running tests with Python 3.9...$(RESET)"
	tox -e py39

.PHONY: test-python310
test-python310: ## test: Run tests with Python 3.10
	@echo "$(BLUE)Running tests with Python 3.10...$(RESET)"
	tox -e py310

.PHONY: test-python311
test-python311: ## test: Run tests with Python 3.11
	@echo "$(BLUE)Running tests with Python 3.11...$(RESET)"
	tox -e py311

.PHONY: test-python312
test-python312: ## test: Run tests with Python 3.12
	@echo "$(BLUE)Running tests with Python 3.12...$(RESET)"
	tox -e py312

# =============================================================================
# CI/CD Integration
# =============================================================================

.PHONY: ci
ci: quality-check test-coverage ## util: Run full CI pipeline
	@echo "$(GREEN)CI pipeline completed successfully$(RESET)"

.PHONY: pre-push
pre-push: quality-check test-fast docs-build ## util: Run checks before pushing
	@echo "$(GREEN)Pre-push checks completed$(RESET)"

.PHONY: release-check
release-check: ci build-check docs-build ## build: Complete release readiness check
	@echo "$(GREEN)Release checks completed$(RESET)"

# =============================================================================
# Development Shortcuts
# =============================================================================

.PHONY: dev
dev: format lint test-fast ## dev: Quick development cycle (format, lint, fast tests)

.PHONY: fix
fix: format pre-commit-run ## dev: Fix common issues automatically

.PHONY: check
check: format-check lint security test-fast ## dev: Check code quality without making changes

.PHONY: full
full: clean install-dev quality-check test-coverage docs-build build-check ## dev: Full development cycle

# =============================================================================
# Platform-specific targets
# =============================================================================

.PHONY: install-windows
install-windows: ## setup: Install Windows-specific dependencies
	@echo "$(BLUE)Installing Windows dependencies...$(RESET)"
	$(PIP) install pywin32 pygetwindow pycaw

.PHONY: install-macos
install-macos: ## setup: Install macOS-specific dependencies
	@echo "$(BLUE)Installing macOS dependencies...$(RESET)"
	$(PIP) install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz pyobjc-framework-ApplicationServices

.PHONY: install-linux
install-linux: ## setup: Install Linux-specific dependencies
	@echo "$(BLUE)Installing Linux dependencies...$(RESET)"
	$(PIP) install python-xlib pycairo pygobject evdev

# =============================================================================
# Special Rules
# =============================================================================

# Prevent make from deleting intermediate files
.SECONDARY:

# Ensure these targets are always run regardless of file timestamps
.PHONY: help setup install run test lint docs build clean ci

# Pattern rule for running specific test files
test-%: ## test: Run specific test file (e.g., make test-core)
	@echo "$(BLUE)Running tests matching pattern: $*$(RESET)"
	pytest -v -k "$*"