.PHONY: build test start start-db

DOCKER ?= $(shell if [ "$$(uname -m)" = "arm64" ]; then echo podman; else echo docker; fi)

build:
	pipenv install --dev

# The postgres image version is read from _infra/postgres-image, which CI uses too.
start-db:
	$(DOCKER) compose --env-file _infra/postgres-image up -d

lint:
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run flake8 --exclude=./scripts

lint-check:
	pipenv run isort . --check-only
	pipenv run black --line-length 120 --check .
	pipenv run flake8 --exclude=./scripts

test: lint-check
	APP_SETTINGS=TestingConfig pipenv run pytest test --cov ras_party --cov-report term-missing

start:
	pipenv run python3 run.py

install:
	pipenv install --dev
