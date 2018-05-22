import logging

import flask
import structlog
from flask import jsonify, Response
from requests import RequestException

from ras_party.exceptions import RasError

logger = structlog.wrap_logger(logging.getLogger(__name__))

blueprint = flask.Blueprint('error_handlers', __name__)


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
    response.status_code = 500
    logger.exception('Uncaught exception', errors=errors, status=500)
    return response


@blueprint.app_errorhandler(Exception)
def exception_error(_):
    logger.exception('Uncaught exception', status=500)
    return Response(status=500)
