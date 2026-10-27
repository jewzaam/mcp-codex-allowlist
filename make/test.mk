.PHONY: test-unit test-coverage test-format test-lint test-typecheck test-complexity test-reachability

test-unit: install-dev  ## Run pytest
	$(PYTHON) -m pytest

test-coverage: install-dev  ## Run pytest with 80% coverage threshold
	$(PYTHON) -m pytest --cov=$(PACKAGE_NAME) --cov-report=term --cov-fail-under=80

test-format: install-dev  ## Check formatting
	$(PYTHON) -m black --check $(PACKAGE_NAME) tests

test-lint: install-dev  ## Lint with flake8
	$(PYTHON) -m flake8 --jobs=1 --max-line-length=88 --extend-ignore=E203,W503 $(PACKAGE_NAME) tests

test-typecheck: install-dev  ## Type check with mypy
	$(PYTHON) -m mypy $(PACKAGE_NAME)

test-complexity: install-dev  ## Check cyclomatic complexity
	$(PYTHON) -m xenon $(PACKAGE_NAME) --max-absolute B --max-modules B --max-average A

test-reachability:  ## Check document reachability
	$(PYTHON) scripts/reachability.py --check
