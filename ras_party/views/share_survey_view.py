import logging

import structlog
from flask import Blueprint, request, make_response, jsonify, current_app
from werkzeug.exceptions import BadRequest

from ras_party.controllers import share_survey_controller
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.validate import Validator, Exists
from ras_party.views.account_view import auth

share_survey_view = Blueprint('share_survey_view', __name__)
logger = structlog.wrap_logger(logging.getLogger(__name__))


@share_survey_view.before_request
@auth.login_required
def before_share_survey_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@share_survey_view.route('/share-survey-users-count', methods=['GET'])
def share_survey_users():
    """
    Get total users count who are already enrolled and pending share survey against business id and survey id
    """
    payload = request.get_json()
    try:
        business_id = payload['business_id']
        survey_id = payload['survey_id']
        # this is just to validate that the business_id exists
        get_business_by_id(business_id)
    except KeyError:
        raise BadRequest('Business Id or survey id is missing')
    response = share_survey_controller.get_users_enrolled_and_pending_share_against_business_and_survey(business_id,
                                                                                                        survey_id)
    return make_response(jsonify(response), 200)


@share_survey_view.route('/pending-shares', methods=['POST'])
def post_business():
    """
     Creates new records for pending shares
     accepted payload example:
     { "business_id": {
            "survey_id": "survey_id",
            "email_address": "email_address"
        },
        "business_id": {
            "survey_id": "survey_id",
            "email_address": "email_address"
        }
     }
    """
    payload = request.get_json() or {}
    for business in payload:
        # Validation, curation and checks
        expected = ('email_address', 'survey_id')

        v = Validator(Exists(*expected))
        if not v.validate(payload[business]):
            logger.debug(v.errors)
            return BadRequest(v.errors)
        for survey in payload:
            share_survey_controller.pending_share_create(business_id=business,
                                                         survey_id=survey,
                                                         email_address=payload[business]['email_address'])
    # TODO: Add logic to send email
    return make_response(jsonify({"created": "success"}), 201)
