import uuid

import itsdangerous
import requests
from flask import current_app
from flask import make_response, jsonify
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import orm
from structlog import get_logger

from ras_party.controllers.error_decorator import translate_exceptions
from ras_party.controllers.ras_error import RasError
from ras_party.controllers.session_context import db_session
from ras_party.controllers.transactional import transactional
from ras_party.controllers.util import build_url
from ras_party.controllers.validate import Validator, IsUuid, Exists, IsIn
from ras_party.models.models import Business, Respondent, BusinessRespondent, Enrolment, RespondentStatus


log = get_logger()

# TODO: consider a decorator to get a db session where needed (maybe replace transaction context mgr)


@translate_exceptions
def get_info():
    info = {
        "name": current_app.config['NAME'],
        "version": current_app.config['VERSION'],
        "origin": "git@github.com:ONSdigital/ras-party.git",
        "commit": "TBD",
        "branch": "TBD",
        "built": "TBD"
    }

    if current_app.config.feature.report_dependencies:
        info["dependencies"] = [{'name': name} for name in current_app.config.dependency.keys()]

    return make_response(jsonify(info), 200)


@translate_exceptions
def businesses_post(business):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param business: Business to add
    :type business: dict | bytes

    :rtype: None
    """
    with db_session() as tran:
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
    v = Validator(Exists('sampleUnitType'), IsIn('sampleUnitType', 'B'))
    if 'id' in party:
        v.add_rule(IsUuid('id'))
    if party['sampleUnitType'] == Business.UNIT_TYPE:
        v.add_rule(Exists('sampleUnitRef'))
    if not v.validate(party):
        return make_response(jsonify(v.errors), 400)

    if party['sampleUnitType'] == Business.UNIT_TYPE:
        with db_session() as tran:
            existing_business = tran.query(Business).filter(Business.business_ref == party['sampleUnitRef']).first()
            if existing_business:
                party['id'] = str(existing_business.party_uuid)
            b = Business.from_party_dict(party)
            if b.valid:
                tran.merge(b)
                return make_response(jsonify(b.to_party_dict()), 200)
            else:
                return make_response(jsonify(b.errors), 400)


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


@translate_exceptions
@transactional
def respondents_post(party, tran):

    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        log.debug(" ID in respondent post message. Adding validation rule IsUuid")
        v.add_rule(IsUuid('id'))

    if not v.validate(party):
        raise RasError(v.errors, 400)

    register_user(party, tran)

    case_context = request_case(party['enrolmentCode'])

    business_id = case_context['partyId']
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    collection_exercise = request_collection_exercise(collection_exercise_id)

    survey_id = collection_exercise['surveyId']
    survey = request_survey(survey_id)

    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'],
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone']
    }

    secret_key = current_app.config["SECRET_KEY"]
    timed_serializer = URLSafeTimedSerializer(secret_key)
    token = timed_serializer.dumps(party['emailAddress'], salt='email-confirm-key')
    frontstage_svc = current_app.config.dependency['frontstage-service']
    frontstage_url = build_url('{}://{}:{}/emailverification/{}', frontstage_svc, token)

    with db_session() as sess:
        try:
            b = sess.query(Business).filter(Business.party_uuid == business_id).one()
        except orm.exc.NoResultFound:
            msg = "Could not locate business with id '{}' when creating business association.".format(business_id)
            raise RasError(msg, status_code=404)

        r = Respondent(**translated_party)
        br = BusinessRespondent(business=b, respondent=r)
        Enrolment(business_respondent=br, survey_id=survey_id)

        sess.add(r)

        return make_response(jsonify(r.to_respondent_dict()), 200)


@translate_exceptions
def put_email_verification(token):
    timed_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    duration = int(current_app.config.get("EMAIL_TOKEN_EXPIRY", '86400'))

    try:
        email_address = timed_serializer.loads(token, salt="email-confirm-key", max_age=duration)
    except itsdangerous.SignatureExpired:
        raise RasError("Verification oken has expired", 409)

    with db_session() as sess:
        try:
            r = sess.query(Respondent).filter(Respondent.email_address == email_address).one()
        except orm.exc.NoResultFound:
            raise RasError("Couldn't locate user.", status_code=404)

        if not r.status == RespondentStatus.CREATED:
            raise RasError("Verification token is invalid or already used.", 409)

        r.status = RespondentStatus.ACTIVE

        return make_response(jsonify(r.to_respondent_dict()), 200)


def register_user(party, tran):
    oauth_payload = {
        "username": party['emailAddress'],
        "password": party['password'],
        "client_id": current_app.config.dependency['oauth2-service']['client_id'],
        "client_secret": current_app.config.dependency['oauth2-service']['client_secret']
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    oauth_response = requests.post(oauth_url, data=oauth_payload)
    if not oauth_response.status_code == 201:
        oauth_response.raise_for_status()

    def dummy_compensating_action():
        """
        TODO: Undo the user registration.
        """
        log.info("Placeholder for deleting the user from oauth-server")

    # Add a compensating action to try and avoid an exception leaving the user in an invalid state.
    tran.compensate(dummy_compensating_action)
    log.info("New user has been registered via the oauth2-service")


def request_case(enrolment_code):
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    response = requests.get(case_url)
    response.raise_for_status()
    return response.json()


def request_collection_exercise(collection_exercise_id):
    ce_svc = current_app.config.dependency['collectionexercise-service']
    ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    response = requests.get(ce_url)
    response.raise_for_status()
    return response.json()


def request_survey(survey_id):
    # TODO: we may want to persist the survey name, otherwise no need to call survey service
    # survey_svc = current_app.config.dependency['survey-service']
    # survey_url = build_url('{}://{}:{}/surveys/{}', survey_svc, survey_id)
    # survey = requests.get(survey_url).json()
    return {}
