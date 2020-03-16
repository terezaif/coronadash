.PHONY: setup
setup:
	poetry config virtualenvs.in-project true
	poetry update
	poetry install --no-interaction --no-ansi


.PHONY: set
set:
	python -m venv env
	env/bin/pip3 install -r requirements.txt