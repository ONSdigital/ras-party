import uuid

import requests
from flask import make_response, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadData, SignatureExpired
from sqlalchemy import orm
from structlog import get_logger
from pathlib import Path
from json import loads

from ras_party.controllers.error_decorator import translate_exceptions
from ras_party.controllers.ras_error import RasError
from ras_party.controllers.session_context import db_session
from ras_party.controllers.transactional import transactional
from ras_party.controllers.util import build_url
from ras_party.controllers.validate import Validator, IsUuid, Exists, IsIn
from ras_party.models.models import Business, Respondent, BusinessRespondent, Enrolment, RespondentStatus, PendingEnrolment, EnrolmentStatus
from ras_party.controllers.gov_uk_notify import GovUKNotify

log = get_logger()

#
#   On the one hand these will be environment dependent and should probably be
#   environment variables, but on the other hand, the requests should be wrapped
#   in error detection and retry code and we shouldn't be relying on these anyway ...
#
REQUESTS_GET_TIMEOUT = 2.0
REQUESTS_POST_TIMEOUT = 2.0

#
#   TODO: the spec seems to read as a need for /info, currently this endpoint responds on /party-api/v1/info
#
_health_check = {}
if Path('git_info').exists():
    with open('git_info') as io:
        _health_check = loads(io.read())

# TODO: consider a decorator to get a db session where needed (maybe replace transaction context mgr)


@translate_exceptions
def get_info():
    info = {
        "name": current_app.config['NAME'],
        "version": current_app.config['VERSION'],
    }
    info = dict(_health_check, **info)

    if current_app.config.feature.report_dependencies:
        info["dependencies"] = [{'name': name} for name in current_app.config.dependency.keys()]

    return make_response(jsonify(info), 200)


def error_result(result):
    """
    Standard error response

    :param result: dictionary containing the error(s)
    :return: valid Flask Response
    """
    log.error(result)
    return make_response(jsonify(result), 400)

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
def businesses_post(json_packet):
    """
    This performs the same function as 'parties_post' except that the data is presented in a 'flat' format.
    As a result, we structure the data, then pass it through to parties_post, setting structured to False
    which forces the resulting output to be presented in the same format we received it. Note; we're not
    necessarily expecting this endpoint to be hit in production.

    :param json_packet: packet containing the data to post
    :type json_packet: JSON data maching the schema described in schemas/party_schema.json
    """
    json_packet = Business.add_structure(json_packet)
    return parties_post(json_packet, structured=False)


@translate_exceptions
def parties_post(json_packet, structured=True):
    """
    Post a new party (with sampleUnitType B)

    :param json_packet: packet containing the data to post
    :type json_packet: JSON data maching the schema described in schemas/party_schema.json
    :param structured: The format we output on completion
    :type bool: Structured or Flat
    """
    result = []
    errors = Business.validate_structured(json_packet)

    if errors:
        [result.append({'message': error.message, 'validator': error.validator}) for error in errors]
        return error_result(result)

    if json_packet['sampleUnitType'] != Business.UNIT_TYPE:
        result.append({'message': 'sampleUnitType must be of type ({})'.format(Business.UNIT_TYPE)})
        return error_result(result)

    with db_session() as tran:
        existing_business = tran.query(Business).filter(Business.business_ref == json_packet['sampleUnitRef']).first()
        if existing_business:
            json_packet['id'] = str(existing_business.party_uuid)
        b = Business.from_party_dict(json_packet)
        tran.merge(b)
        if structured:
            return make_response(jsonify(b.to_structured_dict()), 200)
        else:
            return make_response(jsonify(b.to_flattened_dict()), 200)


@translate_exceptions
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    v = Validator(IsIn('sampleUnitType', 'B'))
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
def get_respondent_by_email(email):
    """
    Get a Respondent by its EMail Address
    Returns a single Party
    :param email: EMail of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    respondent = current_app.db.session.query(Respondent).filter(Respondent.email_address == email).first()
    if not respondent:
        return make_response(jsonify({'errors': "Respondent with email address '{}' does not exist.".format(email)}), 404)

    return make_response(jsonify(respondent.to_respondent_dict()), 200)


@translate_exceptions
@transactional
def respondents_post(party, tran):
    """
    This function is quite complicated, as it performs a number of steps to complete a new respondent enrolment:
    1. Validate the enrolment code and email address
    2. Register the respondent as a new user with the remote OAuth2 service.
    3. Lookup the case context from the case service
    4. Lookup the collection exercise from the collection exercise service
    5. Lookup the survey from the survey service
    6. Generate an email verification token, and an email verification url
    7. Invoke the email verification
    8. Update the database with the new respondent, establishing an association to the business, and an entry
       in the enrolment table (along with the survey id / survey name)
    9. Post a case event to the case service to notify that a new respondent has been created
    10. If something goes wrong after step 1, attempt to perform a compensating action to remove the OAuth2 user
       (this is currently mocked out as the OAuth2 server doesn't implement an endpoint to achieve this)
    """
    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        # Note: there's not strictly a requirement to be able to pass in a UUID, this is currently supported to
        # aid with testing.
        log.debug("ID in respondent post message. Adding validation rule IsUuid")
        v.add_rule(IsUuid('id'))

    if not v.validate(party):
        raise RasError(v.errors, 400)

    iac = request_iac(party['enrolmentCode'])
    if not iac.get('active'):
        raise RasError("Enrolment code is not active.", status_code=400)

    existing = current_app.db.session.query(Respondent)\
        .filter(Respondent.email_address == party['emailAddress'])\
        .first()
    if existing:
        raise RasError("User with email address {} already exists.".format(party['emailAddress']), status_code=400)

    #TODO the register user function needs to handle the tran argument. If there is a failure it knows how to remove the user from the OAuth2 server
    register_user(party, tran)

    #TODO any of the dictionary lookups could return a key error. We should detect and protect against this.
    case_context = request_case(party['enrolmentCode'])
    case_id = case_context['id']
    business_id = case_context['partyId']
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    collection_exercise = request_collection_exercise(collection_exercise_id)

    try:
        survey_id = collection_exercise['surveyId']
        survey = request_survey(survey_id)
        survey_name = survey['longName']
    except KeyError:
        raise RasError("There is no survey bound for this user with email address: {}".format(party['emailAddress']))

    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'],
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone'],
        'status': RespondentStatus.CREATED
    }

    with db_session() as sess:
        try:
            b = sess.query(Business).filter(Business.party_uuid == business_id).one()
        except orm.exc.MultipleResultsFound:
            msg = "There were multiple results found for a business ID while enrolling user with email: {}".format(party['emailAddress'])
            raise RasError(msg, status_code=409)    # TODO This might be better as a 404
        except orm.exc.NoResultFound:
            msg = "Could not locate business with id '{}' when creating business association.".format(business_id)
            raise RasError(msg, status_code=404)

        try:
            #  Create the enrolment respondent-business-survey associations
            r = Respondent(**translated_party)
            br = BusinessRespondent(business=b, respondent=r)
            pending_enrolment = PendingEnrolment(case_id = case_id, respondent=r, business_id=business_id, survey_id = survey_id)
            Enrolment(business_respondent=br, survey_id=survey_id, survey_name=survey_name, status=EnrolmentStatus.PENDING)
            sess.add(r)
            sess.add(pending_enrolment)

            # Notify the case service of this account being created
            post_case_event(case_id, r.party_uuid, "RESPONDENT_ACCOUNT_CREATED", "New respondent account created")

            # Create and send the email verification token
            secret_key = current_app.config["SECRET_KEY"]
            email_token_salt = current_app.config["EMAIL_TOKEN_SALT"] or 'email-confirm-key'
            timed_serializer = URLSafeTimedSerializer(secret_key)
            token = timed_serializer.dumps(party['emailAddress'], salt=email_token_salt)
            frontstage_svc = current_app.config.dependency['frontstage-service']
            frontstage_url = build_url('{}://{}:{}/register/activate-account/{}', frontstage_svc, token)
            notify_service = current_app.config.dependency['gov-uk-notify-service']
            template_id = notify_service['gov_notify_template_id']
            notify(party['emailAddress'], template_id, frontstage_url, r.party_uuid)

        except Exception as e:
            log.error("Could not post the case event, create Enrolement objets, or error in verification email generation. Error is: {}".format(e))

        return make_response(jsonify(r.to_respondent_dict()), 200)

@translate_exceptions
def put_email_verification(token):
    log.info("Verifying email - checking email token: {}".format(token))
    timed_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    duration = int(current_app.config.get("EMAIL_TOKEN_EXPIRY", '86400'))
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"] or 'email-confirm-key'

    try:
        email_address = timed_serializer.loads(token, salt=email_token_salt, max_age=duration)
    except SignatureExpired:
        log.info("An email verification token expired for a user. The token is: {}".format(token))
        raise RasError("Verification token has expired", 409)
    except (BadSignature, BadData) as e:
        log.warning("An email verification token looks like it's corrupt. The token value is: {} and the error is: {}"
                    .format(token, e))
        raise RasError("Email verification is corrupt or does not exist", 404)

    with db_session() as sess:
        try:
            r = sess.query(Respondent).filter(Respondent.email_address == email_address).one()
        except orm.exc.NoResultFound:
            raise RasError("Couldn't locate user.", status_code=404)

        if not r.status == RespondentStatus.CREATED:
            # Do we really want to raise an error if their account is already verified?
            # raise RasError("Verification token is invalid or already used.", 409)
            return make_response(jsonify(r.to_respondent_dict()), 200)

        # We set the party as ACTIVE in this service
        r.status = RespondentStatus.ACTIVE

        # Next we check if this respondent has a pending enrolment (there WILL be only one, set during registration)
        if r.pending_enrolment:
           enrol_respondent_for_survey(r, sess)
        else:
           log.info("No pending enrolment for respondent {}".format(str(r.party_uuid)))

        # We set the user as verified on the OAuth2 server.
        set_user_active(email_address)

        return make_response(jsonify(r.to_respondent_dict()), 200)

# Handle the pending enrolment that was created during registration
def enrol_respondent_for_survey(r, sess):
    # TODO: Need to handle all the DB/SQLAlchemy errors that could occur here!
    pending_enrolment_id = r.pending_enrolment[0].id
    pending_enrolment = sess.query(PendingEnrolment).filter(PendingEnrolment.id == pending_enrolment_id).one()
    enrolment = sess.query(Enrolment).filter(Enrolment.business_id == str(pending_enrolment.business_id)) \
        .filter(Enrolment.survey_id == str(pending_enrolment.survey_id)) \
        .one()
    enrolment.status = EnrolmentStatus.ENABLED
    sess.add(enrolment)
    log.info("Enabling pending enrolment for respondent {} to survey_id {} for business_id {}" \
             .format(str(r.party_uuid), \
                     str(pending_enrolment.survey_id), \
                     str(pending_enrolment.business_id)))
    # Send an enrolment event to the case service
    case_id = pending_enrolment.case_id
    log.info("Pending enrolment for case_id :: " + str(case_id))
    post_case_event(str(case_id), str(r.party_uuid), "RESPONDENT_ENROLED", "Respondent enrolled")
    sess.delete(pending_enrolment)

# Helper function to set the 'active' flag on the OAuth2 server for a user. If it fails a raise_for_status is executed
def set_user_active(respondent_email):

    log.info("Setting user active on OAuth2 server")

    oauth_payload = {
        "username": respondent_email,
        "client_id": current_app.config.dependency['oauth2-service']['client_id'],
        "client_secret": current_app.config.dependency['oauth2-service']['client_secret'],
        "account_verified": "true"
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    oauth_response = requests.put(oauth_url, data=oauth_payload)
    if not oauth_response.status_code == 201:
        log.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()
    log.info("User has been activated on the oauth2 server")


def register_user(party, tran):
    oauth_payload = {
        "username": party['emailAddress'],
        "password": party['password'],
        "client_id": current_app.config.dependency['oauth2-service']['client_id'],
        "client_secret": current_app.config.dependency['oauth2-service']['client_secret']
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    oauth_response = requests.post(oauth_url, data=oauth_payload, timeout=REQUESTS_POST_TIMEOUT)
    if not oauth_response.status_code == 201:
        oauth_response.raise_for_status()

    def dummy_compensating_action():
        """
        TODO: Undo the user registration.
        """
        log.info("Placeholder for deleting the user from oauth server")

    # Add a compensating action to try and avoid an exception leaving the user in an invalid state.
    tran.compensate(dummy_compensating_action)
    log.info("New user has been registered via the oauth2-service")


def request_iac(enrolment_code):
    # TODO: factor out commonality from these request_* functions
    iac_svc = current_app.config.dependency['iac-service']
    iac_url = build_url('{}://{}:{}/iacs/{}', iac_svc, enrolment_code)
    log.info("GET URL {}".format(iac_url))
    response = requests.get(iac_url, timeout=REQUESTS_GET_TIMEOUT)
    log.info("IAC service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_case(enrolment_code):
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    log.info("GET URL {}".format(case_url))
    response = requests.get(case_url, timeout=REQUESTS_GET_TIMEOUT)
    log.info("Case service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_collection_exercise(collection_exercise_id):
    ce_svc = current_app.config.dependency['collectionexercise-service']
    ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    log.info("GET {}".format(ce_url))
    response = requests.get(ce_url, timeout=REQUESTS_GET_TIMEOUT)
    log.info("Collection exercise service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_survey(survey_id):
    survey_svc = current_app.config.dependency['survey-service']
    survey_url = build_url('{}://{}:{}/surveys/{}', survey_svc, survey_id)
    log.info("GET {}".format(survey_url))
    response = requests.get(survey_url, timeout=REQUESTS_GET_TIMEOUT)
    log.info("Survey service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def post_case_event(case_id, party_id, category, desc):
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/{}/events', case_svc, case_id)

    payload = {
        'description': desc ,
        'category': category,
        'partyId': party_id,
        'createdBy': "Party Service"
    }

    log.info("POST {} payload={}".format(case_url, payload))
    response = requests.post(case_url, json=payload, timeout=REQUESTS_POST_TIMEOUT)
    log.info("Case service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()

def notify(email, template_id, url, party_id):
    personalisation = {
        'ACCOUNT_VERIFICATION_URL': url
    }
    log.info("About to send verification email for party_id: {} URL: {}".format(party_id, url))
    if current_app.config.feature['send_email_to_gov_notify']:
        notifier = GovUKNotify()
        notifier.send_message(email, template_id, personalisation, party_id)
    else:
        log.info("Email not sent :: send_email_to_gov_notify=false")

