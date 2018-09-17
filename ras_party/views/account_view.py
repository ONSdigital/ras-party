import logging

import structlog
from flask import Blueprint, request, current_app, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

from ras_party.controllers import account_controller
from ras_party.controllers.validate import Exists, Validator
from ras_party.exceptions import RasError
from ras_party.support.log_decorator import log_route


account_view = Blueprint('account_view', __name__)

logger = structlog.wrap_logger(logging.getLogger(__name__))

auth = HTTPBasicAuth()


@account_view.before_request
@auth.login_required
@log_route
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


@account_view.route('/respondents/change_password/<token>', methods=['PUT'])
def change_respondent_password(token):
    payload = request.get_json() or {}
    response = account_controller.change_respondent_password(token, payload)
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


@account_view.route('/resend-verification-email/<party_uuid>', methods=['GET'])
def resend_verification_email(party_uuid):
    response = account_controller.resend_verification_email_by_uuid(party_uuid)
    return make_response(jsonify(response), 200)


@account_view.route('/resend-verification-email-expired-token/<token>', methods=['GET'])
def resend_verification_email_expired_token(token):
    response = account_controller.resend_verification_email_expired_token(token)
    return make_response(jsonify(response), 200)


@account_view.route('/respondents/add_survey', methods=['POST'])
def respondent_add_survey():
    payload = request.get_json() or {}
    v = Validator(Exists('party_id', 'enrolment_code'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    account_controller.add_new_survey_for_respondent(payload)
    return make_response(jsonify('OK'), 200)


@account_view.route('/respondents/edit-account-status/<party_id>', methods=['PUT'])
def put_respondent_account_status(party_id):
    payload = request.get_json() or {}
    v = Validator(Exists('status_change'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    account_controller.change_respondent_account_status(payload, party_id)
    return make_response(jsonify('OK'), 200)


@account_view.route('/respondents/change_enrolment_status', methods=['PUT'])
def change_respondent_enrolment_status():
    payload = request.get_json() or {}
    v = Validator(Exists('respondent_id', 'business_id', 'survey_id', 'change_flag'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)
    account_controller.change_respondent_enrolment_status(payload)

    return make_response(jsonify('OK'), 200)
