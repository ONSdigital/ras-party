import logging
import structlog
import uuid

from flask import Blueprint, current_app, make_response, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest

from ras_party.controllers import respondent_controller
from ras_party.support.log_decorator import log_route


logger = structlog.wrap_logger(logging.getLogger(__name__))
respondent_view = Blueprint('respondent_view', __name__)
auth = HTTPBasicAuth()


@respondent_view.before_request
@auth.login_required
@log_route
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@respondent_view.route('/respondents', methods=['GET'])
def get_respondents():
    """Get respondents by id or a combination of firstName, lastName and EmailAddress
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
        logger.debug("Invalid params: either id , first_name or last_name or email are required")
        raise BadRequest("id or one of first_name, last_name and email are required")

    if ids and (first_name or last_name or email):
        logger.debug("Invalid params: id not valid with first_name or last_name or email")
        raise BadRequest("id not valid with first_name or last_name or email")

    if ids:
        for party_id in ids:
            try:
                uuid.UUID(party_id)
            except ValueError:
                logger.debug("Invalid params: party_id value is not a valid UUID", party_id=party_id)
                raise BadRequest(f"'{party_id}' is not a valid UUID format for property 'id'")


@respondent_view.route('/respondents/id/<id>', methods=['GET'])
def get_respondent_by_id(id):
    response = respondent_controller.get_respondent_by_id(id)
    return jsonify(response)


@respondent_view.route('/respondents/email', methods=['GET'])
def get_respondent_by_email():
    payload = request.get_json()
    email = payload['email']
    response = respondent_controller.get_respondent_by_email(email)
    return jsonify(response)


@respondent_view.route('/respondents/id/<respondent_id>', methods=['PUT'])
def change_respondent_details(respondent_id):
    payload = request.get_json()
    respondent_controller.change_respondent_details(payload, respondent_id)
    return make_response('Successfully updated respondent details', 200)
