from json import loads
import logging

import structlog
from ras_common_utils.ras_config import ras_config
from retrying import RetryError

from logger_config import logger_initial_config
from run import create_app, initialise_db

"""
This is a duplicate of run.py, with minor modifications to support gunicorn execution.
"""

logger = structlog.wrap_logger(logging.getLogger(__name__))


config_path = 'config/config.yaml'
config = ras_config.from_yaml_file(config_path)

app = create_app(config)
with open(app.config['PARTY_SCHEMA']) as io:
    app.config['PARTY_SCHEMA'] = loads(io.read())

logger_initial_config(service_name='ras-party', log_level=app.config['LOG_LEVEL'])

logger.debug("Created Flask app.")

try:
    initialise_db(app)
except RetryError:
    logger.exception('Failed to initialise database')
    exit(1)

scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])
