# RAS Party

## Overview
This is the RAS Party micro-service. See [Confluence] for further information.


To run the tests with [tox], first ensure you have installed, then simply run the command `tox` in the root of the project.

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


[Confluence]: https://digitaleq.atlassian.net/wiki/display/RASB/Party
[tox]: https://tox.readthedocs.io/en/latest/
