.PHONY: build test start

build:
	pipenv install --dev

lint:
	pipenv check -i 42194 -i 51668 -i 51499 -i 51457
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run flake8 --exclude=./scripts

lint-check:
	pipenv check -i 42194 -i 51668 -i 51499 -i 51457
	pipenv run isort . --check-only
	pipenv run black --line-length 120 --check .
	pipenv run flake8 --exclude=./scripts

test: lint-check
	APP_SETTINGS=TestingConfig pipenv run pytest test --cov ras_party --cov-report term-missing

start:
	pipenv run python3 run.py
