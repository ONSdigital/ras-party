from flask import Blueprint, request, current_app, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

import ras_party.controllers.party_controller
from ras_party.support.log_decorator import log_route

party_view = Blueprint('party_view', __name__)


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@party_view.route('/businesses', methods=['POST'])
@auth.login_required
@log_route
def post_business():
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.businesses_post(payload)
    return make_response(jsonify(response), 200)


@party_view.route('/businesses/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_id(id):
    response = ras_party.controllers.party_controller.get_business_by_id(id)
    return make_response(jsonify(response), 200)


@party_view.route('/businesses/ref/<ref>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_ref(ref):
    response = ras_party.controllers.party_controller.get_business_by_ref(ref)
    return make_response(jsonify(response), 200)


@party_view.route('/parties', methods=['POST'])
@auth.login_required
@log_route
def post_party():
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.parties_post(payload)
    return make_response(jsonify(response), 200)


@party_view.route('/parties/type/<sampleUnitType>/ref/<sampleUnitRef>', methods=['GET'])
@auth.login_required
@log_route
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    response = ras_party.controllers.party_controller.get_party_by_ref(sampleUnitType, sampleUnitRef)
    return make_response(jsonify(response), 200)


@party_view.route('/parties/type/<sampleUnitType>/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_party_by_id(sampleUnitType, id):
    response = ras_party.controllers.party_controller.get_party_by_id(sampleUnitType, id)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_respondent_by_id(id):
    response = ras_party.controllers.party_controller.get_respondent_by_id(id)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents/email/<string:token>', methods=['GET'])
@auth.login_required
@log_route
def get_respondent_by_email(token):
    response = ras_party.controllers.party_controller.get_respondent_by_email(token)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents/change_email', methods=['PUT'])
@party_view.route('/respondents/email', methods=['PUT'])
@auth.login_required
@log_route
def put_respondent_by_email():
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.change_respondent(payload)
    return make_response(jsonify(response), 200)


@party_view.route('/tokens/verify/<token>', methods=['GET'])
@auth.login_required
@log_route
def get_verify_token(token):
    response = ras_party.controllers.party_controller.verify_token(token)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents/change_password/<token>', methods=['PUT'])
@auth.login_required
@log_route
def change_respondent_password(token):
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.change_respondent_password(token, payload)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents/request_password_change', methods=['POST'])
@auth.login_required
@log_route
def post_respondent_reset_password_by_email():
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.request_password_change(payload)
    return make_response(jsonify(response), 200)


@party_view.route('/respondents', methods=['POST'])
@auth.login_required
@log_route
def post_respondent():
    payload = request.get_json() or {}
    response = ras_party.controllers.party_controller.post_respondent(payload)
    return make_response(jsonify(response), 200)


@party_view.route('/emailverification/<token>', methods=['PUT'])
@auth.login_required
@log_route
def put_email_verification(token):
    response = ras_party.controllers.party_controller.put_email_verification(token)
    return make_response(jsonify(response), 200)


@party_view.route('/resend-verification-email/<party_uuid>', methods=['GET'])
@auth.login_required
@log_route
def resend_verification_email(party_uuid):
    response = ras_party.controllers.party_controller.resend_verification_email(party_uuid)
    return make_response(jsonify(response), 200)
