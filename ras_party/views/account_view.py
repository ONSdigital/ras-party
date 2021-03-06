import logging

import structlog
from flask import Blueprint, request, current_app, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest

from ras_party.controllers import account_controller
from ras_party.controllers.validate import Exists, Validator


account_view = Blueprint('account_view', __name__)

logger = structlog.wrap_logger(logging.getLogger(__name__))

auth = HTTPBasicAuth()


@account_view.before_request
@auth.login_required
def before_account_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@account_view.route('/respondents/change_email', methods=['PUT'])
@account_view.route('/respondents/email', methods=['PUT'])
def put_respondent_by_email():
    payload = request.get_json() or {}
    response = account_controller.change_respondent(payload)
    return make_response(jsonify(response), 200)


@account_view.route('/tokens/verify/<token>', methods=['GET'])
def get_verify_token(token):
    response = account_controller.verify_token(token)
    return make_response(jsonify(response), 200)


@account_view.route('/respondents/change_password', methods=['PUT'])
def change_respondent_password():
    payload = request.get_json() or {}
    response = account_controller.change_respondent_password(payload)
    return make_response(jsonify(response), 200)


@account_view.route('/respondents/request_password_change', methods=['POST'])
def post_respondent_reset_password_by_email():
    payload = request.get_json() or {}
    response = account_controller.request_password_change(payload)
    return make_response(jsonify(response), 200)


@account_view.route('/respondents', methods=['POST'])
def post_respondent():
    payload = request.get_json() or {}
    response = account_controller.post_respondent(payload)
    return make_response(jsonify(response), 200)


@account_view.route('/emailverification/<token>', methods=['PUT'])
def put_email_verification(token):
    response = account_controller.put_email_verification(token)
    return make_response(jsonify(response), 200)


@account_view.route('/resend-verification-email/<party_uuid>', methods=['POST'])
def resend_verification_email(party_uuid):
    response = account_controller.resend_verification_email_by_uuid(party_uuid)
    return make_response(jsonify(response), 200)


@account_view.route('/resend-verification-email-expired-token/<token>', methods=['POST'])
def resend_verification_email_expired_token(token):
    response = account_controller.resend_verification_email_expired_token(token)
    return make_response(jsonify(response), 200)


@account_view.route('/resend-password-email-expired-token/<token>', methods=['POST'])
def resend_password_email_expired_token(token):
    response = account_controller.resend_password_email_expired_token(token)
    return make_response(jsonify(response), 200)


@account_view.route('/respondents/add_survey', methods=['POST'])
def respondent_add_survey():
    payload = request.get_json() or {}
    v = Validator(Exists('party_id', 'enrolment_code'))
    if not v.validate(payload):
        logger.debug(v.errors, url=request.url)
        raise BadRequest(v.errors)

    account_controller.add_new_survey_for_respondent(payload)
    return make_response(jsonify('OK'), 200)


@account_view.route('/respondents/change_enrolment_status', methods=['PUT'])
def change_respondent_enrolment_status():
    payload = request.get_json() or {}
    v = Validator(Exists('respondent_id', 'business_id', 'survey_id', 'change_flag'))
    if not v.validate(payload):
        logger.debug(v.errors, url=request.url)
        raise BadRequest(v.errors)
    account_controller.change_respondent_enrolment_status(payload)

    return make_response(jsonify('OK'), 200)


@account_view.route('/respondents/disable-user-enrolments', methods=['PATCH'])
def disable_user_enrolments():
    """Disable all enrolments for a specific respondent email address"""
    try:
        email = request.get_json()['email']
    except TypeError:
        raise BadRequest('JSON payload not provided')
    except KeyError:
        raise BadRequest("Email key must be provided in the JSON payload")

    removed_enrolment_count = account_controller.disable_all_respondent_enrolments(email)

    return make_response(jsonify({"message": f'{removed_enrolment_count} enrolments removed'}), 200)


@account_view.route('/respondents/edit-account-status/<party_id>', methods=['PUT'])
def put_edit_account_status(party_id):
    # This is the party endpoint to lock and notify respondent when account is locked
    # This is also the end point for internal user to unlock a respondents account
    payload = request.get_json() or {}
    v = Validator(Exists('status_change'))
    if not v.validate(payload):
        logger.debug(v.errors, url=request.url)
        raise BadRequest(v.errors)

    response = account_controller.notify_change_account_status(payload=payload, party_id=party_id)
    return make_response(jsonify(response), 200)
