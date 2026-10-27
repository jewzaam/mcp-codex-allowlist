.PHONY: check help clean format install install-dev install-pipx uninstall uninstall-pipx

PACKAGE_NAME ?= mcp_codex_allowlist
PROJECT_NAME ?= mcp-codex-allowlist
PY_SYS ?= python3
HOME_DIR := $(subst \,/,$(HOME))

ifeq ($(OS),Windows_NT)
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/mcp/Scripts/python.exe),$(HOME_DIR)/.venv/mcp,.venv)
    PYTHON ?= $(VENV_DIR)/Scripts/python.exe
else
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/mcp/bin/python),$(HOME_DIR)/.venv/mcp,.venv)
    PYTHON ?= $(VENV_DIR)/bin/python
endif

-include make/test.mk

$(info venv: $(VENV_DIR))

check: test-format test-lint test-typecheck test-unit test-coverage test-reachability  ## Run full quality gate (default)

.DEFAULT_GOAL := check

help:  ## Show available targets
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-32s\033[0m %s\n", $$1, $$2}'

$(PYTHON):
	$(PY_SYS) -m venv $(VENV_DIR)

clean:  ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

format: install-dev  ## Format source and tests
	$(PYTHON) -m black $(PACKAGE_NAME) tests

install: $(PYTHON)  ## Install into the local virtual environment
	$(PYTHON) -m pip install .

install-dev: $(PYTHON)  ## Install editable package and development tools
	$(PYTHON) -m pip install -e ".[dev]"

install-pipx:  ## Install globally via pipx
	python3 -m pipx install . --force

uninstall: $(PYTHON)  ## Uninstall from the local virtual environment
	$(PYTHON) -m pip uninstall -y $(PROJECT_NAME)

uninstall-pipx:  ## Uninstall the pipx install
	python3 -m pipx uninstall $(PROJECT_NAME)
