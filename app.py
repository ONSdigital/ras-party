import requests
from json import loads
import logging

import structlog

from retrying import RetryError
from flask_zipkin import Zipkin

from logger_config import logger_initial_config
from run import create_app, initialise_db

"""
This is a duplicate of run.py, with minor modifications to support gunicorn execution.
"""

logger = structlog.wrap_logger(logging.getLogger(__name__))

app = create_app()

# Zipkin
zipkin = Zipkin(app=app, sample_rate=app.config.get("ZIPKIN_SAMPLE_RATE"))
original_prepare_headers = requests.models.PreparedRequest.prepare_headers


def new_prepare_headers(self, headers):
    defaults = zipkin.create_http_headers_for_new_span()

    if headers is not None:
        defaults.update(headers)

    original_prepare_headers(self, defaults)


requests.models.PreparedRequest.prepare_headers = new_prepare_headers

with open(app.config['PARTY_SCHEMA']) as io:
    app.config['PARTY_SCHEMA'] = loads(io.read())

logger_initial_config(service_name='ras-party', log_level=app.config['LOGGING_LEVEL'])

logger.debug("Created Flask app.")

try:
    initialise_db(app)
except RetryError:
    logger.exception('Failed to initialise database')
    exit(1)

scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])
