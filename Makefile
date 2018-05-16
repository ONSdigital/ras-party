.PHONY: build lint start test

build:
	pipenv install --dev

lint:
	pipenv run flake8 ./ras_party ./test

test: lint
	pipenv run tox

start:
	pipenv run python3 run.py
