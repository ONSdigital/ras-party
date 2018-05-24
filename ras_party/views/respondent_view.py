from flask import Blueprint, current_app, make_response, jsonify, request
from flask_httpauth import HTTPBasicAuth

from ras_party.exceptions import RasError
from ras_party.controllers import respondent_controller
from ras_party.support.log_decorator import log_route

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
    ids = request.args.getlist("id")
    if ids:
        # with_db_session function wrapper automatically injects the session parameter
        # pylint: disable=maybe-no-member
        response = respondent_controller.get_respondent_by_ids(ids)
    else:
        raise RasError("The parameter id is required.", status=400)

    return jsonify(response)


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
