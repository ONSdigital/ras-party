import uuid
import json
import requests
from flask import make_response, jsonify, current_app

from swagger_server.controllers.error_decorator import translate_exceptions
from swagger_server.controllers.session_context import transaction
from swagger_server.controllers.validate import Validator, IsIn, Exists, IsUuid
from swagger_server.models.models import Business, Respondent
from structlog import get_logger
from flask import current_app

logger = get_logger()

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


#@translate_exceptions
def respondents_post(party):

    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        logger.debug(" ID in respondent post message. Adding validation rule IsUuid")
        v.add_rule(IsUuid('id'))

    if not v.validate(party):
        logger.info("Validation failed for respondent [POST] Message.")
        logger.info("Validation errors from [POST] are: {}".format(v.errors))
        return make_response(jsonify(v.errors), 400)

    # TODO: refactor code to separate service calls
    # Validation passed. Let's create this user on the OAuth2 server.
    # 1) Send a POST message to create a user on OAuth2 server
    #   User                FS                  PS                      OAuth2
    #   ----                --                  --                      ------
    #     create-account    |
    #   ------------------->|
    #                       |   create-account  |
    #                       | ----------------->|    api/account/create   |
    #                       |                   | ----------------------->|
    logger.debug("Validation is complete for respondents_post")
    print("*** Validation is complete for respondents_post")
    for key in party:
        print ("key is: {}".format(key))
        print ("value is: {}".format(party[key]))

    # print variables out
    #print ("oauth2 scheme is: {}".format(current_app.config['scheme']))
    #print ("client id is: {}".format(current_app.config['dependencies']['oauth2']['client_id']))
    #print ("client secret is: {}".format(current_app.config['client_secret']))
    #print ("Oauth2 host is: {}".format(current_app.config['host']))
    #print ("Oauth2 port is: {}".format(current_app.config['port']))
    #print ("admin endpoint is: {}".format(current_app.config['admin_endpoint']))
    #print ("token endpoint is: {}".format(current_app.config['token_endpoint']))


    OAuth_payload = {
        "username": party['emailAddress'],
        "password": party['password'],
        #"client_id": current_app.config['client_id'],
        #"client_secret": current_app.config['client_secret']
        "client_id": "ons@ons.gov",
        "client_secret": "password"
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}

    #authorisation = {current_app.config.dependencies.oauth2['client_id']: current_app.config.dependencies.oauth2['client_secret']}
    authorisation = {'ons@ons.gov': 'password'}

    print ("Ready to talk to OAuth2 server...")

    try:
        #OAuthurl = current_app.config['scheme'] + current_app.config['host'] + current_app.config['port'] + current_app.config['admin_endpoint']
        OAuthurl = "http://localhost:8001/api/account/create"
        print ("OAuthurl is: {}".format(OAuthurl))
        #OAuth_response = requests.post(OAuthurl, auth=authorisation, headers=headers, data=OAuth_payload)

        OAuth_response = requests.post(OAuthurl, data=OAuth_payload)

        logger.debug("OAuth response is: {}".format(OAuth_response.content))

        # json.loads(myResponse.content.decode('utf-8'))
        response_body = json.loads(OAuth_response.content.decode('utf-8'))
        logger.debug("OAuth2 response is: {}".format(OAuth_response.status_code))

        if OAuth_response.status_code == 401:
            # This looks like the user is not authorized to use the system. it could be a duplicate email. check our
            # exact error. if it is, then tell the user else fail as our server is not allowed to access the OAuth2
            # system.
            # TODO add logging
            # {"detail":"Duplicate user credentials"}
            if response_body["detail"]:
                if response_body["detail"] == 'Duplicate user credentials':
                    logger.warning("We have duplicate user credentials")
                    errors = {'email_address_confirm': ['Please try a different email, this one is in use', ]}
                    return make_response(jsonify(errors), 400)

        # Deal with all other errors from OAuth2 registration
        if OAuth_response.status_code > 401:
            OAuth_response.raise_for_status()  # A stop gap until we know all the correct error pages
            logger.warning("OAuth error")

        # TODO A utility function to allow us to route to a page for 'user is registered already'.
        # We need a html page for this.

    except requests.exceptions.ConnectionError:
        logger.critical("There seems to be no server listening on this connection?")
        errors = {'connection error': 'There is no network connectivity to the OAuth2 server on this connection:{} '.format(OAuthurl)}
        return make_response(jsonify(errors), 400)

    except requests.exceptions.Timeout:
        logger.critical("Timeout error. Is the OAuth Server overloaded?")
        errors = {'connection error': 'The OAuth2 server is not responding on this connection:{} '.format(OAuthurl)}
        return make_response(jsonify(errors), 400)

        # TODO A redirect to a page that helps the user
    except requests.exceptions.RequestException as e:
        # TODO catastrophic error. bail. A page that tells the user something horrid has happened and who to inform
        print ("something bad just happened! ")
        logger.debug(e)




    enrolment_code = party['enrolmentCode']
    print ("Enrolement code is: {}".format(enrolment_code))
    logger.info("EnrolementCode for respondent [POST] is: {} ".format(enrolment_code))
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    resp = requests.get(case_url)
    case_context = resp.json()

    # TODO: consider error scenarios
    # collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    # ce_svc = current_app.config.dependency['collectionexercise-service']
    # ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    # resp = requests.get(ce_url)
    # collection_exercise = resp


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
        'party_uuid': party.get('id') or uuid.uuid4(),
        'email_address': party['emailAddress'],
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone']
    }
    with transaction() as tran:
        r = Respondent(**translated_party)
        tran.merge(r)
        return make_response(jsonify(r.to_respondent_dict()), 200)
