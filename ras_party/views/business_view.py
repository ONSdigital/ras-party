from flask import Blueprint, request, make_response, current_app, jsonify
from flask_httpauth import HTTPBasicAuth

import ras_party.controllers.account_controller
import ras_party.controllers.business_controller
import ras_party.controllers.party_controller
import ras_party.controllers.respondent_controller
from ras_party.support.log_decorator import log_route

business_view = Blueprint('business_view', __name__)


auth = HTTPBasicAuth()


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@business_view.route('/businesses', methods=['POST'])
@auth.login_required
@log_route
def post_business():
    payload = request.get_json() or {}
    response = ras_party.controllers.business_controller.businesses_post(payload)
    return make_response(jsonify(response), 200)


@business_view.route('/businesses/id/<id>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_id(id):
    verbose = request.args.get('verbose', '')
    verbose = True if verbose and verbose.lower() == 'true' else False

    response = ras_party.controllers.business_controller.get_business_by_id(id, verbose=verbose)
    return make_response(jsonify(response), 200)


@business_view.route('/businesses/ref/<ref>', methods=['GET'])
@auth.login_required
@log_route
def get_business_by_ref(ref):
    verbose = request.args.get('verbose', '')
    verbose = True if verbose and verbose.lower() == 'true' else False

    response = ras_party.controllers.business_controller.get_business_by_ref(ref, verbose=verbose)
    return make_response(jsonify(response), 200)