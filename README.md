# RAS Party

## Overview
This is the RAS Party micro-service. See [Confluence] for further information.

The API is specified [here](./API.md).

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

## Running
[Install Docker](https://docs.docker.com/engine/installation/)
```bash
docker-compose up
```

To test the service is up:

```
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

The database will automatically be created when starting the application.


[Confluence]: https://digitaleq.atlassian.net/wiki/display/RASB/Party
[tox]: https://tox.readthedocs.io/en/latest/
