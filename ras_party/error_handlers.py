import logging

import flask
import structlog
from flask import jsonify
from requests import RequestException

from ras_party.exceptions import ClientError, RasError

logger = structlog.wrap_logger(logging.getLogger(__name__))

blueprint = flask.Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(ClientError)
def client_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logger.info('Client error', errors=error.to_dict(), status=error.status_code)
    return response


@blueprint.app_errorhandler(RasError)
def ras_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    logger.exception('Uncaught exception', errors=error.to_dict(), status=error.status_code)
    return response


@blueprint.app_errorhandler(RequestException)
def http_error(error):
    errors = {'errors': {'method': error.request.method, 'url': error.request.url, }}
    response = jsonify(errors)
    if error.response is not None:
        response.status_code = error.response.status_code
    else:
        response.status_code = 500
    logger.exception('Uncaught exception', errors=errors, status=response.status_code)
    return response


@blueprint.app_errorhandler(Exception)
def exception_error(_):
    logger.exception('Uncaught exception', status=500)
    response = jsonify({})
    response.status_code = 500
    return response
