from flask import Blueprint, request

from swagger_server.controllers import controller

party_view = Blueprint('party_views', __name__)


# TODO: unify this code with the controller

@party_view.route('/businesses', methods=['POST'])
def post_business():
    payload = request.json
    return controller.businesses_post(payload)


@party_view.route('/businesses/id/<id>', methods=['GET'])
def get_business_by_id(id):
    return controller.get_business_by_id(id)


@party_view.route('/businesses/ref/<ref>', methods=['GET'])
def get_business_by_ref(ref):
    return controller.get_business_by_ref(ref)


@party_view.route('/parties', methods=['POST'])
def post_party():
    payload = request.json
    return controller.parties_post(payload)


@party_view.route('/parties/type/<sampleUnitType>/ref/<sampleUnitRef>', methods=['GET'])
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    return controller.get_party_by_ref(sampleUnitType, sampleUnitRef)


@party_view.route('/parties/type/<sampleUnitType>/id/<id>', methods=['GET'])
def get_party_by_id(sampleUnitType, id):
    return controller.get_party_by_id(sampleUnitType, id)


@party_view.route('/respondents/id/<id>', methods=['GET'])
def get_respondent_by_id(id):
    return controller.get_respondent_by_id(id)


@party_view.route('/respondents', methods=['POST'])
def post_respondent():
    payload = request.json
    return controller.respondents_post(payload)
