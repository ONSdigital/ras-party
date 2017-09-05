from flask import Blueprint, request, current_app
from flask_httpauth import HTTPBasicAuth

from ras_party.controllers import controller
from ras_party.controllers.log_decorator import log_route

party_view = Blueprint('party_view', __name__)


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


# TODO: unify this code with the controller


@party_view.route('/businesses', methods=['POST'])
@auth.login_required
@log_route
def post_business():
    payload = request.get_json() or {}
    return controller.businesses_post(payload)


@party_view.route('/businesses/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_id(id):
    return controller.get_business_by_id(id)


@party_view.route('/businesses/ref/<ref>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_ref(ref):
    return controller.get_business_by_ref(ref)


@party_view.route('/parties', methods=['POST'])
@auth.login_required
@log_route
def post_party():
    payload = request.get_json() or {}
    return controller.parties_post(payload)


@party_view.route('/parties/type/<sampleUnitType>/ref/<sampleUnitRef>', methods=['GET'])
@auth.login_required
@log_route
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    return controller.get_party_by_ref(sampleUnitType, sampleUnitRef)


@party_view.route('/parties/type/<sampleUnitType>/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_party_by_id(sampleUnitType, id):
    return controller.get_party_by_id(sampleUnitType, id)


@party_view.route('/respondents/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_respondent_by_id(id):
    return controller.get_respondent_by_id(id)


@party_view.route('/respondents/email/<email>', methods=['GET'])
@auth.login_required
@log_route
def get_respondent_by_email(email):
    return controller.get_respondent_by_email(email)


@party_view.route('/respondents', methods=['POST'])
@auth.login_required
@log_route
def post_respondent():
    payload = request.get_json() or {}
    return controller.respondents_post(payload)


@party_view.route('/emailverification/<token>', methods=['PUT'])
@auth.login_required
@log_route
def put_email_verification(token):
    return controller.put_email_verification(token)


@party_view.route('/resend-verification-email/<party_uuid>', methods=['GET'])
@auth.login_required
@log_route
def resend_verification_email(party_uuid):
    return controller.resend_verification_email(party_uuid)
