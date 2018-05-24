from flask import Blueprint, request, current_app, jsonify
from flask_httpauth import HTTPBasicAuth

from ras_party.exceptions import RasError
from ras_party.controllers import business_controller
from ras_party.support.log_decorator import log_route


business_view = Blueprint('business_view', __name__)
auth = HTTPBasicAuth()


@business_view.before_request
@auth.login_required
@log_route
def before_business_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@business_view.route('/businesses', methods=['POST'])
def post_business():
    payload = request.get_json() or {}
    response = business_controller.businesses_post(payload)
    return jsonify(response)


@business_view.route('/businesses', methods=['GET'])
def get_businesses():
    ids = request.args.getlist("id")
    if ids:
        # with_db_session function wrapper automatically injects the session parameter
        # pylint: disable=no-value-for-parameter
        response = business_controller.get_businesses_by_ids(ids)
    else:
        raise RasError("The parameter id is required.", status=400)

    return jsonify(response)


@business_view.route('/businesses/id/<business_id>', methods=['GET'])
def get_business_by_id(business_id):
    verbose = request.args.get('verbose', '')
    verbose = True if verbose and verbose.lower() == 'true' else False

    response = business_controller.get_business_by_id(business_id, verbose=verbose,
                                                      collection_exercise_id=request.args.get('collection_exercise_id'))
    return jsonify(response)


@business_view.route('/businesses/ref/<ref>', methods=['GET'])
def get_business_by_ref(ref):
    verbose = request.args.get('verbose', '')
    verbose = True if verbose and verbose.lower() == 'true' else False

    response = business_controller.get_business_by_ref(ref, verbose=verbose)
    return jsonify(response)


@business_view.route('/businesses/sample/link/<sample>', methods=['PUT'])
def put_business_attributes_ce(sample):
    payload = request.get_json() or {}
    business_controller.businesses_sample_ce_link(sample, payload)

    response = {**payload, "sampleSummaryId": sample}
    return jsonify(response)


@business_view.route('/businesses/search', methods=['GET'])
def get_party_by_search():
    query = request.args.get('query', '')

    response = business_controller.get_businesses_by_search_query(query)
    return jsonify(response)
