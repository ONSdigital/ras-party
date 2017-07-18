# RAS Party

## Overview
This is the RAS Party micro-service. See [Confluence] for further information.

The API is specified [here](./API.md).


## Tests
To run the tests with [tox], install tox (see link) then simply run the command `tox` in the root of the project.
tox will create a unique virtualenv, run the unit tests with py.test, then run flake8 coverage.

To install and run: Create a (Python 3.5+) virtualenv, then:
``` bash
pip install -r requirements.txt
python run.py
```

To test the service is up:

```
curl http://localhost:8080/party-api/v1/info
```

## Database

The database will automatically be created when starting the application.


[Confluence]: https://digitaleq.atlassian.net/wiki/display/RASB/Party
[tox]: https://tox.readthedocs.io/en/latest/
