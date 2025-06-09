.PHONY: lint format check test

lint:
	ruff check --fix .

format:
	ruff format .

check:
	mypy src --strict

test:
	pytest tests/ -v

all: lint format check test 