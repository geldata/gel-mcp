.PHONY: lint format check

lint:
	ruff check --fix .

format:
	ruff format .

check:
	mypy src --strict

all: lint format check 