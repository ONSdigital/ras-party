from flask import Blueprint, request, current_app, jsonify
from flask_httpauth import HTTPBasicAuth

from ras_party.controllers import party_controller
from ras_party.support.log_decorator import log_route


party_view = Blueprint('party_view', __name__)
auth = HTTPBasicAuth()


@party_view.before_request
@auth.login_required
@log_route
def before_party_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@party_view.route('/parties', methods=['POST'])
def post_party():
    payload = request.get_json() or {}
    response = party_controller.parties_post(payload)
    return jsonify(response)


@party_view.route('/parties/ref/<sample_unit_ref>', methods=['GET'])
def get_party_by_ref(sample_unit_ref):
    response = party_controller.get_party_by_ref(sample_unit_ref)
    return jsonify(response)


@party_view.route('/parties/id/<id>', methods=['GET'])
def get_party_by_id(id):
    survey_id = request.args.get('survey_id')
    enrolment_status = request.args.get('enrolment_status')

    if survey_id:
        response = party_controller.get_party_with_enrolments_filtered_by_survey(id, survey_id, enrolment_status)
    else:
        response = party_controller.get_party_by_id(id)

    return jsonify(response)
