#!/bin/bash
if ! [ -a .build-test ] ; then
	echo "Creating Virtual Environment"
	virtualenv .build-test -p python3
fi
source .build-test/bin/activate
pip3 -q install -r test-requirements.txt
pytest swagger_server/test_local --cov=swagger_server/controllers_local --cov-report term-missing
