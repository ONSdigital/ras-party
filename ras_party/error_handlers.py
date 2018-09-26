import logging

import flask
import structlog
from flask import jsonify, request
from requests import RequestException
from werkzeug.exceptions import HTTPException


logger = structlog.wrap_logger(logging.getLogger(__name__))

blueprint = flask.Blueprint('error_handlers', __name__)


@blueprint.app_errorhandler(HTTPException)
def http_exception_handler(error):
    response = jsonify({"description": error.description})
    response.status_code = error.code
    return response


@blueprint.app_errorhandler(RequestException)
def http_error(error):
    errors = {'errors': {'method': error.request.method, 'url': error.request.url, }}
    response = jsonify(errors)
    if error.response is not None:
        response.status_code = error.response.status_code
    else:
        response.status_code = 500
    logger.exception('Error requesting another service',
                     url=request.url,
                     errors=errors,
                     status=response.status_code)
    return response


@blueprint.app_errorhandler(Exception)
def exception_error(_):
    logger.exception('Uncaught exception', status=500)
    response = jsonify({})
    response.status_code = 500
    return response
