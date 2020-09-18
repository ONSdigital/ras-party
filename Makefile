.PHONY: build test start

build:
	pipenv install --dev

test:
	APP_SETTINGS=TestingConfig pipenv run pytest test --cov ras_party --cov-report term-missing

start:
	pipenv run python3 run.py
