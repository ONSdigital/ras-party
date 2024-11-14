import logging

import structlog
from flask import Blueprint, Response, current_app, make_response, request
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers.enrolments_controller import enrolments_by_parameters

logger = structlog.wrap_logger(logging.getLogger(__name__))
enrolments_view = Blueprint("enrolments_view", __name__)
auth = HTTPBasicAuth()


@enrolments_view.before_request
@auth.login_required
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password


@enrolments_view.route("/enrolments", methods=["GET"])
def get_enrolments() -> Response:
    json = request.get_json()
    party_uuid = json.get("party_uuid")
    business_id = json.get("business_id")
    survey_id = json.get("survey_id")
    status = json.get("status")

    if not (party_uuid or business_id or survey_id):
        logger.error("No parameters passed to get_enrolments")
        return BadRequest()

    try:
        enrolments = enrolments_by_parameters(
            party_uuid=party_uuid, business_id=business_id, survey_id=survey_id, status=status
        )
    except NoResultFound:
        logger.error(f"Respondent not found for party_uuid {party_uuid}")
        return NotFound()
    except DataError:
        logger.error(
            "Data error, enrolment search parameters are not valid",
            party_uuid=party_uuid,
            business_id=business_id,
            survey_id=survey_id,
            status=status,
        )
        return BadRequest()

    return make_response([enrolment.to_dict() for enrolment in enrolments], 200)
