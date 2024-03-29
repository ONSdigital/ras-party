import logging
from json import loads

import structlog
from retrying import RetryError

from logger_config import logger_initial_config
from run import create_app, initialise_db

"""
This is a duplicate of run.py, with minor modifications to support gunicorn execution
"""

logger = structlog.wrap_logger(logging.getLogger(__name__))

app = create_app()

with open(app.config["PARTY_SCHEMA"]) as io:
    app.config["PARTY_SCHEMA"] = loads(io.read())

logger_initial_config(log_level=app.config["LOGGING_LEVEL"])

logger.debug("Created Flask app.")

try:
    initialise_db(app)
except RetryError:
    logger.exception("Failed to initialise database")
    exit(1)

scheme, host, port = app.config["SCHEME"], app.config["HOST"], int(app.config["PORT"])
