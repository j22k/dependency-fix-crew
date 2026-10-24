PY ?= python

.PHONY: install run-concierge run-scanner run-advisory run-fixer test lint

install:
	$(PY) -m pip install -r requirements.txt

run-concierge:
	$(PY) -m agents.concierge

run-scanner:
	$(PY) -m agents.scanner

run-advisory:
	$(PY) -m agents.advisory

run-fixer:
	$(PY) -m agents.fixer

test:
	$(PY) -m pytest tests

lint:
	$(PY) -m ruff check .
