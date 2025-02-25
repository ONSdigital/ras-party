import logging
from uuid import UUID

import structlog
from flask import Blueprint, Response, current_app, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest

from ras_party.controllers import respondent_controller
from ras_party.controllers.enrolments_controller import is_respondent_enrolled
from ras_party.uuid_helper import is_valid_uuid4

logger = structlog.wrap_logger(logging.getLogger(__name__))
respondent_view = Blueprint("respondent_view", __name__)
auth = HTTPBasicAuth()


@respondent_view.before_request
@auth.login_required
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password


@respondent_view.route("/respondents", methods=["GET"])
def get_respondents():
    """Get respondents by id or any/all of firstName, lastName and EmailAddress
    Note, result set for names and email includes total record count to support pagination, get by id does not
    """

    ids = request.args.getlist("id")
    first_name = request.args.get("firstName", default="").strip()
    last_name = request.args.get("lastName", default="").strip()
    email = request.args.get("emailAddress", default="").strip()
    page = int(request.args.get("page", default=1))
    limit = int(request.args.get("limit", default=10))

    _validate_get_respondent_params(ids, first_name, last_name, email)
    # with_db_session function wrapper automatically injects the session parameter
    # pylint: disable=no-value-for-parameter
    if ids:
        response = respondent_controller.get_respondent_by_ids(ids)
    else:
        response = respondent_controller.get_respondents_by_name_and_email(first_name, last_name, email, page, limit)
    return jsonify(response)


def _validate_get_respondent_params(ids, first_name, last_name, email):
    """
    Validates the combination of parameters for get respondents
    :param ids:
    :param first_name:
    :param last_name:
    :param email:
    """

    if not (ids or first_name or last_name or email):
        logger.info("Invalid params: either id , first_name or last_name or email are required")
        raise BadRequest("id or one of first_name, last_name and email are required")

    if ids and (first_name or last_name or email):
        logger.info("Invalid params: id not valid with first_name or last_name or email")
        raise BadRequest("id not valid with first_name or last_name or email")

    if ids:
        for party_id in ids:
            try:
                UUID(party_id)
            except ValueError:
                logger.info("Invalid params: party_id value is not a valid UUID", party_id=party_id)
                raise BadRequest(f"'{party_id}' is not a valid UUID format for property 'id'")


@respondent_view.route("/respondents/party_id/<party_id>", methods=["GET"])
def get_respondent_by_party_id(party_id: UUID) -> Response:
    if not is_valid_uuid4(party_id):
        return make_response("party_id is not UUID", 400)

    respondent = respondent_controller.get_respondent_by_party_id(party_id)
    if respondent:
        return make_response(respondent.to_respondent_dict(), 200)

    return make_response(f"respondent not found for party_id {party_id}", 404)


@respondent_view.route("/respondents/id/<respondent_id>", methods=["GET"])
def get_respondent_by_id(respondent_id):
    response = respondent_controller.get_respondent_by_id(respondent_id)
    return jsonify(response)


@respondent_view.route("/respondents/email", methods=["GET"])
def get_respondent_by_email():
    payload = request.get_json()
    email = payload["email"]
    response = respondent_controller.get_respondent_by_email(email)
    return jsonify(response)


@respondent_view.route("/respondents/<email>", methods=["DELETE"])
def delete_respondent_by_email(email):
    response = respondent_controller.update_respondent_mark_for_deletion(email)
    return response


@respondent_view.route("/respondents/id/<respondent_id>", methods=["PUT"])
def change_respondent_details(respondent_id):
    payload = request.get_json()
    respondent_controller.change_respondent_details(payload, respondent_id)
    return make_response("Successfully updated respondent details", 200)


@respondent_view.route("/respondents/claim")
def validate_respondent_claim():
    """Validates if the respondent has a claim on a specific business and survey
    Both valid and invalid claims return 200 with the difference being indicated in the response body.

    Not RESTFUL style more like RPC, but the alternative is for duplication of business logic
    in client services. There is an argument to use a 403 on invalid claims , but that should be a status on the
    resource not the state of the returned data and so that's stretching the use of http status codes somewhat
    """
    party_uuid = request.args.get("respondent_id")
    business_id = request.args.get("business_id")
    survey_id = request.args.get("survey_id")

    if not (is_valid_uuid4(party_uuid) and is_valid_uuid4(business_id) and is_valid_uuid4(survey_id)):
        return make_response("Bad request, party_uuid, business or survey id not UUID", 400)

    if is_respondent_enrolled(party_uuid, business_id, survey_id):
        return make_response("Valid", 200)

    return make_response("Invalid", 200)


@respondent_view.route("/respondents/survey_id/<survey_id>/business_id/<business_id>", methods=["GET"])
def get_respondents_by_business_and_survey_id(business_id: UUID, survey_id: UUID) -> Response:
    """Gets a list of Respondents enrolled in a survey for a specified business"""

    if not (is_valid_uuid4(survey_id) and is_valid_uuid4(business_id)):
        return make_response("Bad request, business or survey id not UUID", 400)

    respondents = respondent_controller.get_respondents_by_survey_and_business_id(survey_id, business_id)
    return make_response(respondents, 200)
