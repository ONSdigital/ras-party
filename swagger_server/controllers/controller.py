import uuid

import requests
from flask import make_response, jsonify, current_app

from swagger_server.controllers.error_decorator import translate_exceptions
from swagger_server.controllers.session_context import transaction
from swagger_server.controllers.validate import Validator, IsIn, Exists, IsUuid
from swagger_server.models.models import Business, Respondent, BusinessRespondent, Enrolment


# TODO: consider a decorator to get a db session where needed (maybe replace transaction context mgr)


@translate_exceptions
def businesses_post(business):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param business: Business to add
    :type business: dict | bytes

    :rtype: None
    """
    with transaction() as tran:
        if 'businessRef' in business:
            existing_business = tran.query(Business).filter(Business.business_ref == business['businessRef']).first()
            if existing_business:
                business['id'] = str(existing_business.party_uuid)

        b = Business.from_business_dict(business)
        if b.valid:
            tran.merge(b)
            return make_response(jsonify(b.to_business_dict()), 200)
        else:
            return make_response(jsonify(b.errors), 400)


@translate_exceptions
def get_business_by_id(id):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param id: ID of Party to return
    :type id: str

    :rtype: Business
    """

    v = Validator(IsUuid('id'))
    if not v.validate({'id': id}):
        return make_response(jsonify(v.errors), 400)

    business = current_app.db.session.query(Business).filter(Business.party_uuid == id).first()
    if not business:
        return make_response(jsonify({'errors': "Business with party id '{}' does not exist.".format(id)}), 404)

    return make_response(jsonify(business.to_business_dict()), 200)


@translate_exceptions
def get_business_by_ref(ref):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """
    business = current_app.db.session.query(Business).filter(Business.business_ref == ref).first()
    if not business:
        return make_response(jsonify({'errors': "Business with reference '{}' does not exist.".format(ref)}), 404)

    return make_response(jsonify(business.to_business_dict()), 200)


@translate_exceptions
def parties_post(party):
    """
    given a sampleUnitType B | H this adds a reporting unit of type Business or Household
    Adds a new Party of type sampleUnitType or updates an existing Party based on the reference provided
    :param party: Party to add
    :type party: dict | bytes

    :rtype: None
    """
    v = Validator(Exists('sampleUnitType'), IsIn('sampleUnitType', 'B', 'BI'))
    if 'id' in party:
        v.add_rule(IsUuid('id'))
    if party['sampleUnitType'] == Business.UNIT_TYPE:
        v.add_rule(Exists('sampleUnitRef'))
    if not v.validate(party):
        return make_response(jsonify(v.errors), 400)

    if party['sampleUnitType'] == Business.UNIT_TYPE:
        with transaction() as tran:
            existing_business = tran.query(Business).filter(Business.business_ref == party['sampleUnitRef']).first()
            if existing_business:
                party['id'] = str(existing_business.party_uuid)
            b = Business.from_party_dict(party)
            tran.merge(b)
            return make_response(jsonify(b.to_party_dict()), 200)
    else:
        return make_response(jsonify({'errors': "Unknown sampleUnitType '{}'".format(party['sampleUnitType'])}), 400)


@translate_exceptions
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sampleUnitType}):
        return make_response(jsonify(v.errors), 400)

    business = current_app.db.session.query(Business).filter(Business.business_ref == sampleUnitRef).first()
    if not business:
        return make_response(jsonify(
            {'errors': "Business with reference '{}' does not exist.".format(sampleUnitRef)}), 404)

    return make_response(jsonify(business.to_party_dict()), 200)


@translate_exceptions
def get_party_by_id(sampleUnitType, id):
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sampleUnitType}):
        return make_response(jsonify(v.errors), 400)

    if sampleUnitType == Business.UNIT_TYPE:
        business = current_app.db.session.query(Business).filter(Business.party_uuid == id).first()
        if not business:
            return make_response(jsonify({'errors': "Business with id '{}' does not exist.".format(id)}), 404)

        return make_response(jsonify(business.to_party_dict()), 200)

    elif sampleUnitType == Respondent.UNIT_TYPE:
        respondent = current_app.db.session.query(Respondent).filter(Respondent.party_uuid == id).first()
        if not respondent:
            return make_response(jsonify({'errors': "Respondent with id '{}' does not exist.".format(id)}), 404)

        return make_response(jsonify(respondent.to_party_dict()), 200)


@translate_exceptions
def get_respondent_by_id(id):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    v = Validator(IsUuid('id'))
    if not v.validate({'id': id}):
        return make_response(jsonify(v.errors), 400)

    respondent = current_app.db.session.query(Respondent).filter(Respondent.party_uuid == id).first()
    if not respondent:
        return make_response(jsonify({'errors': "Respondent with party id '{}' does not exist.".format(id)}), 404)

    return make_response(jsonify(respondent.to_respondent_dict()), 200)


class MockConfig:

    def __init__(self):
        self._case_service = {'scheme': 'http', 'host': 'localhost', 'port': '8171'}

    def dependency(self, _):
        return self._case_service


def build_url(template, config, *args):
    url = template.format(config['scheme'], config['host'], config['port'], *args)
    return url


@translate_exceptions
def respondents_post(party):

    expected = ('emailAddress', 'firstName', 'lastName', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        v.add_rule(IsUuid('id'))

    if not v.validate(party):
        return make_response(jsonify(v.errors), 400)

    # TODO: refactor code to separate service calls
    enrolment_code = party['enrolmentCode']
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    case_context = requests.get(case_url).json()
    business_party_uuid = case_context['partyId']

    # TODO: consider error scenarios
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    ce_svc = current_app.config.dependency['collectionexercise-service']
    ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    collection_exercise = requests.get(ce_url).json()

    survey_id = collection_exercise['surveyId']
    survey_svc = current_app.config.dependency['survey-service']
    survey_url = build_url('{}://{}:{}/surveys/{}', survey_svc, survey_id)
    survey = requests.get(survey_url).json()

    """ TODO:
    GET /collectionexercises/{uuid}
    GET /surveys/{uuid}
    create business_respondent association
    create enrolment (between business_respondent + survey id)
    POST account created case event
    create uuid / email verification link
    persist the email verification link
    call gov.uk notify (see Mark's branch)
    map route to accept verified email, and enable account
    """

    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'],
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone']
    }
    with transaction() as tran:

        b = tran.query(Business).filter(Business.party_uuid == business_party_uuid).one()
        r = Respondent(**translated_party)

        br = BusinessRespondent(business=b, respondent=r)
        e = Enrolment(business_respondent=br, survey_id=survey['id'])

        tran.merge(r)   # TODO: is it still ok to do a merge here?
        tran.add(br)
        tran.add(e)
        return make_response(jsonify(r.to_respondent_dict()), 200)
