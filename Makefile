# Makefile for gitb
# Usage examples:
#   make venv
#   make lint
#   make fmt
#   make test
#   make run CMD="AleixMT --exclude-gitlab"
#   make clean

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# ---- config ---------------------------------------------------------------

# Check if python3.14 exists, otherwise default to python3
ifneq ($(shell command -v python3.14 2> /dev/null),)
    PYTHON_BIN ?= python3.14
else
    PYTHON_BIN ?= python3
endif

VENV_DIR   ?= venv
VENV_BIN   ?= $(VENV_DIR)/bin
PYTHON     := $(VENV_BIN)/python
PIP        := $(VENV_BIN)/pip
PRE_COMMIT := $(VENV_BIN)/pre-commit

PKG_NAME   := gitb

# ---- build ----------------------------------------------------------------

dist: $(VENV_BIN)/pyproject-build ## Build source and wheel distribution
	@$(PYTHON) -m build

# ---- helpers --------------------------------------------------------------

# Create virtualenv
$(VENV_BIN)/python:
	@$(PYTHON_BIN) -m venv "$(VENV_DIR)"
	@$(PYTHON_BIN) -m pip install --upgrade pip

# Install runtime dependencies (creates gitb executable)
$(VENV_BIN)/gitb: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e .

# Install dev dependencies
# We use a stamp file as the target because the gitb executable is also produced by
# 'make install', and binaries like 'bin/ruff' might not have their timestamp updated
# by pip if they are already present (which would cause 'make fmt && make lint' to reinstall).
$(VENV_DIR)/.installed-dev: $(VENV_BIN)/python pyproject.toml
	@$(PIP) install -e ".[dev]"
	@if [ -f .pre-commit-config.yaml ]; then $(PRE_COMMIT) install; fi
	@touch "$@"

# Install build tool
$(VENV_BIN)/pyproject-build: $(VENV_BIN)/python
	@$(PIP) install build

# Phony aliases
venv: $(VENV_BIN)/python  ## Create virtualenv
	@echo "✅ venv ready at $(VENV_DIR)"

install: $(VENV_BIN)/gitb  ## Install package in editable mode

dev: $(VENV_DIR)/.installed-dev  ## Install package and dev dependencies

# ---- quality --------------------------------------------------------------

lint: dev  ## Run static checks (ruff + mypy)
	@$(VENV_BIN)/ruff check .
	@$(VENV_BIN)/mypy src

fmt: dev  ## Auto-format (black + ruff --fix)
	@$(VENV_BIN)/black src $(wildcard tests)
	@$(VENV_BIN)/ruff check --fix .

test: dev  ## Run tests
	@PYTHONUNBUFFERED=1 $(VENV_BIN)/pytest -s

# ---- run ------------------------------------------------------------------

# Pass arguments to the CLI via CMD, e.g.:
#   make run CMD="AleixMT --exclude-gitlab"
CMD ?= --help
run: install  ## Run the gitb CLI (python -m gitb)
	@PYTHONUNBUFFERED=1 $(PYTHON) -m $(PKG_NAME) $(CMD)

# ---- maintenance ----------------------------------------------------------

clean:  ## Remove build/test artifacts
	@rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info src/*.egg-info "$(VENV_DIR)"

# ---- meta -----------------------------------------------------------------

.PHONY: venv lint fmt test run clean help dist install dev

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
