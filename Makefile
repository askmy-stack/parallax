.PHONY: help install lint typecheck test format ci clean

help:
	@echo "Targets: install lint typecheck test format ci clean"

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

typecheck:
	mypy agentfailbench runtime recovery baselines

test:
	pytest

ci: lint typecheck test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
