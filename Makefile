.PHONY: setup
setup:
	poetry config virtualenvs.in-project true
	poetry update
	poetry install --no-interaction --no-ansi
