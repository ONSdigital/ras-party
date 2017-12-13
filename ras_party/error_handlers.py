import logging

import flask
import structlog
from flask import jsonify
from requests import HTTPError

from ras_party.exceptions import RasError

log = structlog.wrap_logger(logging.getLogger(__name__))

blueprint = flask.Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(Exception)
def exception_error(error):
    response = jsonify({'errors': error if type(error) is list else [error]})
    response.status_code = 500
    return response


@blueprint.app_errorhandler(HTTPError)
def http_error(error):
    detail = error.response.json().get('detail', "No further detail.")
    response = jsonify({'errors': [str(error), detail]})
    response.status_code = 500
    return response


@blueprint.app_errorhandler(RasError)
def ras_error(error):
    log.error(error.to_dict())
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
