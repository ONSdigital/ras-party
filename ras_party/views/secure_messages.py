from ras_party.controllers.secure_message_controller import get_respondent_by_ids
import logging
from uuid import UUID

import structlog
from flask import Blueprint, Response, current_app, make_response, request
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers.enrolments_controller import (
    is_respondent_enrolled,
    respondent_enrolments,
)
from ras_party.uuid_helper import is_valid_uuid4

logger = structlog.wrap_logger(logging.getLogger(__name__))
secure_messages_view = Blueprint("secure_messages_view", __name__)
auth = HTTPBasicAuth()


@secure_messages_view.before_request
@auth.login_required
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password



@secure_messages_view.route("/", methods=["GET"])
def get_secure_message_details() -> Response:
    payload = request.get_json()

    respondents = get_respondent_by_ids(payload)

    return make_response(respondents, 200)
