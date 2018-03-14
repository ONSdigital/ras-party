.PHONY: build lint start

build:
	pipenv install --dev

lint:
	pipenv run flake8 ./ras_party ./test
	pipenv check ./ras_party ./test

start:
	pipenv run python3 run.py
