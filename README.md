# RAS Party

## Overview
This is the RAS Party micro-service. See [Confluence] for further information.


## Tests
To run the tests with [tox], install tox (see link) then simply run the command `tox` in the root of the project.
tox will create a unique virtualenv, run the unit tests with py.test, then run flake8 coverage.

To install and run. Firstly create a virtualenv, then:
``` bash
pip3 install -r requirements.txt
python3 -m swagger_server
```

and open your browser to here:

```
http://localhost:8080/party-api/1.0.0/ui/
```

Your Swagger definition lives here:

```
http://localhost:8080/party-api/1.0.0/swagger.json
```

## Database

The database will automatically be created when starting the application. It is also possible to drop/create the
database via create_db.py. Run `python create_db.py` in the project root to see further guidance.


[Confluence]: https://digitaleq.atlassian.net/wiki/display/RASB/Party
[tox]: https://tox.readthedocs.io/en/latest/
