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

Note: Acceptance tests can be run to populate a local version with test data

## Tests

Ensure dev dependencies have been installed

```bash
pipenv install --dev
```

Run tests with makefile

```bash
make test
```

## Database

The database will automatically be created when starting the application
Alembic is used for database migrations
See [README.md](https://github.com/ONSdigital/ras-party/blob/master/migrations/README.md) for alembic documentation

See [Confluence](https://digitaleq.atlassian.net/wiki/display/RASB/Party) for additional information.

## Configuration
Environment variables available for configuration are listed below:

| Environment Variable            | Description                                                   | Default
|---------------------------------|---------------------------------------------------------------|-------------------------------
| LOGGING_LEVEL                   | Level of the logging                                          | 'INFO'
| DATABASE_URI                    | URI used to connect to the database                           | 'postgresql://postgres:postgres@localhost:6432/postgres'
| AUTH_SERVICE_URL                | URL of the auth service                                       |
| CASE_SERVICE_URL                | URL of the case service                                       |
| COLLECTION_EXERCISE_SERVICE_URL | URL of the collection exercise service                        |
| FRONTSTAGE_URL                  | URL of the respondent facing website                          |
| IAC_SERVICE_URL                 | URL of the iac service                                        |
| SURVEY_SERVICE_URL              | URL of the survey service                                     |
| NOTIFY_SERVICE_URL              | URL of the notify-gateway service                             | 'http://notify-gateway-service/emails/
