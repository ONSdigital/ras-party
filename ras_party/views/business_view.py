from functools import partial
from flask import Blueprint, current_app
from flask_httpauth import HTTPBasicAuth
from concurrent import futures

from aiohttp import web
import asyncio

from ras_party.exceptions import RasError
from ras_party.controllers.business_controller import businesses_post, get_business_with_id, businesses_sample_ce_link
from ras_party.support.log_decorator import log_route


executor = futures.ThreadPoolExecutor()

# auth = HTTPBasicAuth()
#
#
# @auth.get_password
# async def get_pw(username):
#     config_username = current_app.config['SECURITY_USER_NAME']
#     config_password = current_app.config['SECURITY_USER_PASSWORD']
#     if username == config_username:
#         return config_password


# @auth.login_required
@log_route
async def post_business(request):
    payload = await request.json()
    response = await asyncio.get_event_loop().run_in_executor(executor,
                                                              partial(businesses_post, payload, request.db))
    return web.json_response(response)

#
# @business_view.route('/businesses', methods=['GET'])
# def get_businesses():
#     ids = request.args.getlist("id")
#     if ids:
#         # with_db_session function wrapper automatically injects the session parameter
#         # pylint: disable=no-value-for-parameter
#         response = business_controller.get_businesses_by_ids(ids)
#     else:
#         raise RasError("The parameter id is required.", status=400)
#
#     return jsonify(response)


# @auth.login_required
# @log_route
async def get_business_by_id(request):
    verbose = request.rel_url.query.get('verbose', '')
    verbose = True if verbose and verbose.lower() == 'true' else False
    party_uuid = request.match_info['business_id']
    response = await asyncio.get_event_loop().run_in_executor(executor, partial(get_business_with_id, party_uuid, request.db, verbose=verbose,
                                                                                collection_exercise_id=request.rel_url.query.get('collection_exercise_id')))
    if not response:
        raise RasError("Business with party id does not exist.", party_uuid=party_uuid, status=404)
    return web.json_response(response)

#
# @business_view.route('/businesses/ref/<ref>', methods=['GET'])
# def get_business_by_ref(ref):
#     verbose = request.args.get('verbose', '')
#     verbose = True if verbose and verbose.lower() == 'true' else False
#
#     response = business_controller.get_business_by_ref(ref, verbose=verbose)
#     return jsonify(response)
#
#


# @auth.login_required
# @log_route
async def put_business_attributes_ce(request):
    sample = request.match_info['sample']
    payload = await request.json()
    await asyncio.get_event_loop().run_in_executor(executor, partial(businesses_sample_ce_link, sample, payload, request.db))

    response = {**payload, "sampleSummaryId": sample}
    return web.json_response(response)
#
#
# @business_view.route('/businesses/search', methods=['GET'])
# def get_party_by_search():
#     query = request.args.get('query', '')
#
#     response = business_controller.get_businesses_by_search_query(query)
#     return jsonify(response)
