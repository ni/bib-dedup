.PHONY: help venv install install-dev test run

PYTHON := .venv/bin/python
PIP := .venv/bin/python -m pip

help:
	@echo "Targets:"
	@echo "  make venv         Create .venv"
	@echo "  make install      Install bib-dedup (editable)"
	@echo "  make install-dev  Install bib-dedup + dev deps (editable)"
	@echo "  make test         Run pytest"
	@echo "  make run ARGS=... Run bib-dedup with ARGS"

venv:
	python3 -m venv .venv
	$(PIP) install -U pip

install: venv
	$(PIP) install -e .

install-dev: venv
	$(PIP) install -e ".[dev]"

test: install-dev
	$(PYTHON) -m pytest

run: install
	.venv/bin/bib-dedup $(ARGS)
