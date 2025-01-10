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


@enrolments_view.route("/respondent/<party_uuid>", methods=["GET"])
def get_respondent_enrolments(party_uuid: UUID) -> Response:
    json = request.get_json()
    business_id = json.get("business_id")
    survey_id = json.get("survey_id")
    status = json.get("status")

    if not is_valid_uuid4(party_uuid):
        logger.error(f"party_id not a valid uuid {party_uuid}")
        return BadRequest()

    try:
        enrolments = respondent_enrolments(
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

    return make_response(enrolments, 200)


@enrolments_view.route(
    "/is_respondent_enrolled/<party_uuid>/business_id/<business_id>/survey_id/<survey_id>", methods=["GET"]
)
def get_is_respondent_enrolled(party_uuid: UUID, business_id: UUID, survey_id: UUID) -> Response:
    if not (is_valid_uuid4(party_uuid) and is_valid_uuid4(business_id) and is_valid_uuid4(survey_id)):
        return make_response("Bad request, party_uuid, business or survey id not UUID", 400)

    enrolled_status = is_respondent_enrolled(party_uuid=party_uuid, business_id=business_id, survey_id=survey_id)
    if enrolled_status:
        return make_response({"enrolled": True}, 200)
    return make_response({"enrolled": False}, 200)
