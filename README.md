# RAS Party

## Overview

This is the RAS Party micro-service. See [Confluence] for further information

The API is specified [here](./API.md)

## Setup

Install postgresql

```bash
brew install postgresql
```

Install pipenv

```bash
pip install pipenv
```

Use pipenv to create a virtualenv and install dependencies

```bash
pipenv install
```

you can also use the makefile to do this

```bash
make install
```

## Running

[Install Docker](https://docs.docker.com/engine/installation/)

```bash
docker-compose up
```

or use the makefile to run

```bash
make start
```

or run locally (this requires postgres running locally on port 5432):

```bash
pipenv run python3 run.py
```

To test the service is up:

```bash
curl http://localhost:8081/info
```

## Tests

Ensure dev dependencies have been installed

```bash
pipenv install --dev
```

Run tests with tox

```bash
pipenv run tox
```

## Database

The database will automatically be created when starting the application
Alembic is used for database migrations
See [README.md](https://github.com/ONSdigital/ras-party/blob/master/migrations/README.md) for alembic documentation

[Confluence]: https://digitaleq.atlassian.net/wiki/display/RASB/Party
[tox]: https://tox.readthedocs.io/en/latest/
