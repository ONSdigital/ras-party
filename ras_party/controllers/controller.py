import uuid
from json import loads
from pathlib import Path

from flask import make_response, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadData, SignatureExpired
from ras_common_utils.ras_error.ras_error import RasError, RasNotifyError
from sqlalchemy import orm
from structlog import get_logger

from ras_party.controllers.error_decorator import translate_exceptions
from ras_party.controllers.gov_uk_notify import GovUKNotify
from ras_party.controllers.requests_wrapper import Requests
from ras_party.controllers.session_decorator import with_db_session
from ras_party.controllers.transactional import transactional
from ras_party.controllers.util import build_url
from ras_party.controllers.validate import Validator, IsUuid, Exists, IsIn
from ras_party.models.models import Business, Respondent, BusinessRespondent, Enrolment, RespondentStatus, \
    PendingEnrolment, EnrolmentStatus

log = get_logger()

#
#   On the one hand these will be environment dependent and should probably be
#   environment variables, but on the other hand, the requests should be wrapped
#   in error detection and retry code and we shouldn't be relying on these anyway ...
#

NO_RESPONDENT_FOR_PARTY_ID = 'There is no respondent with that party ID '
EMAIL_ALREADY_VERIFIED = 'The Respondent for that party ID is already verified'
EMAIL_VERIFICATION_SEND = 'A new verification email has been sent'
EMAIL_CHANGED = 'Respondents email has been changed'

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


def error_result(errors):
    """
    Standard error response

    :param errors: list of error messages
    :return: valid Flask Response
    """
    # TODO: standard error handling should be migrated to error decorator (invoked via raising an exception)
    messages = [{'message': error.message, 'validator': error.validator} for error in errors]
    log.error(messages)
    return make_response(jsonify(messages), 400)


@translate_exceptions
@with_db_session
def get_business_by_ref(ref, session):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """
    business = session.query(Business).filter(Business.business_ref == ref).first()
    if not business:
        return make_response(jsonify({'errors': "Business with reference '{}' does not exist.".format(ref)}), 404)

    return make_response(jsonify(business.to_business_dict()), 200)


@translate_exceptions
@with_db_session
def get_business_by_id(id, session):
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

    business = session.query(Business).filter(Business.party_uuid == id).first()
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
    :type json_packet: JSON data matching the schema described in schemas/party_schema.json
    """
    json_packet = Business.add_structure(json_packet)
    return parties_post(json_packet, structured=False)


@translate_exceptions
@with_db_session
def parties_post(json_packet, session, structured=True):
    """
    Post a new party (with sampleUnitType B)

    :param json_packet: packet containing the data to post
    :type json_packet: JSON data maching the schema described in schemas/party_schema.json
    :param structured: The format we output on completion
    :type bool: Structured or Flat
    """
    errors = Business.validate(json_packet, current_app.config['PARTY_SCHEMA'])
    if errors:
        return error_result(errors)

    if json_packet['sampleUnitType'] != Business.UNIT_TYPE:
        return error_result([{'message': 'sampleUnitType must be of type ({})'.format(Business.UNIT_TYPE)}])

    existing_business = session.query(Business).filter(Business.business_ref == json_packet['sampleUnitRef']).first()
    if existing_business:
        json_packet['id'] = str(existing_business.party_uuid)

    b = Business.from_party_dict(json_packet)
    session.merge(b)
    resp = b.to_party_dict() if structured else b.to_business_dict()
    return make_response(jsonify(resp), 200)


@translate_exceptions
@with_db_session
def get_party_by_ref(sample_unit_type, sample_unit_ref, session):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    v = Validator(IsIn('sampleUnitType', 'B'))
    if not v.validate({'sampleUnitType': sample_unit_type}):
        return make_response(jsonify(v.errors), 400)

    business = session.query(Business).filter(Business.business_ref == sample_unit_ref).first()
    if not business:
        return make_response(jsonify(
            {'errors': "Business with reference '{}' does not exist.".format(sample_unit_ref)}), 404)

    return make_response(jsonify(business.to_party_dict()), 200)


@translate_exceptions
@with_db_session
def get_party_by_id(sample_unit_type, id, session):
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sample_unit_type}):
        return make_response(jsonify(v.errors), 400)

    if sample_unit_type == Business.UNIT_TYPE:
        business = session.query(Business).filter(Business.party_uuid == id).first()
        if not business:
            return make_response(jsonify({'errors': "Business with id '{}' does not exist.".format(id)}), 404)

        return make_response(jsonify(business.to_party_dict()), 200)

    elif sample_unit_type == Respondent.UNIT_TYPE:
        respondent = session.query(Respondent).filter(Respondent.party_uuid == id).first()
        if not respondent:
            return make_response(jsonify({'errors': "Respondent with id '{}' does not exist.".format(id)}), 404)

        return make_response(jsonify(respondent.to_party_dict()), 200)


@translate_exceptions
@with_db_session
def get_respondent_by_id(id, session):
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

    respondent = session.query(Respondent).filter(Respondent.party_uuid == id).first()
    if not respondent:
        return make_response(jsonify({'errors': "Respondent with party id '{}' does not exist.".format(id)}), 404)

    return make_response(jsonify(respondent.to_respondent_dict()), 200)


@translate_exceptions
@with_db_session
def get_respondent_by_email(email, session):
    """
    Get a Respondent by its EMail Address
    Returns a single Party
    :param email: EMail of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    respondent = session.query(Respondent).filter(Respondent.email_address == email).first()
    if not respondent:
        return make_response(jsonify({'errors': "Respondent does not exist."}), 404)

    return make_response(jsonify(respondent.to_respondent_dict()), 200)


@translate_exceptions
@transactional
@with_db_session
def respondents_post(party, tran, session):
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

    existing = session.query(Respondent) \
        .filter(Respondent.email_address == party['emailAddress']) \
        .first()
    if existing:
        raise RasError("User with email address {} already exists.".format(party['emailAddress']), status_code=400)

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

    try:
        b = session.query(Business).filter(Business.party_uuid == business_id).one()
    except orm.exc.MultipleResultsFound:
        # FIXME: this is not possible - party_uuid is a unique key
        msg = "There were multiple results found for a business ID while enrolling user with email: {}" \
            .format(party['emailAddress'])
        raise RasError(msg, status_code=409)  # TODO This might be better as a 404
    except orm.exc.NoResultFound:
        msg = "Could not locate business with id '{}' when creating business association.".format(business_id)
        raise RasError(msg, status_code=404)

    try:
        #  Create the enrolment respondent-business-survey associations
        r = Respondent(**translated_party)
        br = BusinessRespondent(business=b, respondent=r)
        pending_enrolment = PendingEnrolment(case_id=case_id,
                                             respondent=r,
                                             business_id=business_id,
                                             survey_id=survey_id)
        Enrolment(business_respondent=br,
                  survey_id=survey_id,
                  survey_name=survey_name,
                  status=EnrolmentStatus.PENDING)
        session.add(r)
        session.add(pending_enrolment)

        # Notify the case service of this account being created
        post_case_event(case_id, r.party_uuid, "RESPONDENT_ACCOUNT_CREATED", "New respondent account created")

        _send_email_verification(r.party_uuid, party['emailAddress'])
    except (orm.exc.ObjectDeletedError, orm.exc.FlushError, orm.exc.StaleDataError, orm.exc.DetachedInstanceError):
        msg = "Error updating database for user id: {} ".format(party['id'])
        raise RasError(msg, status_code=500)
    except KeyError:
        msg = "Missing config keys during enrolment"
        raise RasError(msg, status_code=500)
    except Exception as e:
        msg = "Error during enrolment process {}".format(e)
        raise RasError(msg, status_code=500)

    register_user(party, tran)

    return make_response(jsonify(r.to_respondent_dict()), 200)


@translate_exceptions
@with_db_session
def put_email_verification(token, session):
    # TODO Add some doc string or comments.
    log.info("Checking email verification token: {}".format(token))
    timed_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    duration = int(current_app.config.get("EMAIL_TOKEN_EXPIRY", '86400'))
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"] or 'email-confirm-key'

    try:
        email_address = timed_serializer.loads(token, salt=email_token_salt, max_age=duration)
    except SignatureExpired:
        msg = "Expired email verification token {}".format(token)
        raise RasError(msg, 409)
    except (BadSignature, BadData) as e:
        msg = "Bad email verification token {} error {}".format(token, e)
        raise RasError(msg, 404)

    try:
        r = session.query(Respondent).filter(Respondent.email_address == email_address).one()
    except orm.exc.NoResultFound:
        raise RasError("Unable to find user while checking email verification token", status_code=404)

    if r.status == RespondentStatus.ACTIVE:
        return make_response(jsonify(r.to_respondent_dict()), 200)

    # We set the party as ACTIVE in this service
    r.status = RespondentStatus.ACTIVE

    # Next we check if this respondent has a pending enrolment (there WILL be only one, set during registration)
    # TODO: Think about adding transaction to this function
    if r.pending_enrolment:
        enrol_respondent_for_survey(r, session)
    else:
        log.info("No pending enrolment for respondent {} while checking email verification token"
                 .format(str(r.party_uuid)))

    # We set the user as verified on the OAuth2 server.
    set_user_verified(email_address)
    return make_response(jsonify(r.to_respondent_dict()), 200)


def set_user_verified(respondent_email):
    """ Helper function to set the 'verified' flag on the OAuth2 server for a user.
        If it fails a raise_for_status is executed
    """
    log.info("Setting user active on OAuth2 server")

    client_id = current_app.config.dependency['oauth2-service']['client_id']
    client_secret = current_app.config.dependency['oauth2-service']['client_secret']

    oauth_payload = {
        "username": respondent_email,
        "client_id": client_id,
        "client_secret": client_secret,
        "account_verified": "true"
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    auth = (client_id, client_secret)
    oauth_response = Requests.put(oauth_url, auth=auth, data=oauth_payload)
    if not oauth_response.status_code == 201:
        log.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()
    log.info("User has been activated on the oauth2 server")


def set_user_unverified(respondent_email):
    """ Helper function to set the 'verified' flag on the OAuth2 server for a user.
        If it fails a raise_for_status is executed
    """
    log.info("Setting user unverified on OAuth2 server")
    oauth_response = update_user_verification(respondent_email, 'true')
    if not oauth_response.status_code == 201:
        log.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()
    log.info("User has been activated on the oauth2 server")


def update_user_verification(respondent_email, verified):
    client_id = current_app.config.dependency['oauth2-service']['client_id']
    client_secret = current_app.config.dependency['oauth2-service']['client_secret']

    oauth_payload = {
        "username": respondent_email,
        "client_id": client_id,
        "client_secret": client_secret,
        "account_verified": verified
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    auth = (client_id, client_secret)
    response = Requests.put(oauth_url, auth=auth, data=oauth_payload)
    return response


# Handle the pending enrolment that was created during registration
def enrol_respondent_for_survey(r, sess):
    # TODO: Need to handle all the DB/SQLAlchemy errors that could occur here!
    # TODO: comments and explanation
    pending_enrolment_id = r.pending_enrolment[0].id
    pending_enrolment = sess.query(PendingEnrolment).filter(PendingEnrolment.id == pending_enrolment_id).one()
    enrolment = sess.query(Enrolment)\
        .filter(Enrolment.business_id == str(pending_enrolment.business_id))\
        .filter(Enrolment.survey_id == str(pending_enrolment.survey_id)) \
        .filter(Enrolment.respondent_id == r.id).one()
    enrolment.status = EnrolmentStatus.ENABLED
    sess.add(enrolment)
    log.info("Enabling pending enrolment for respondent {} to survey_id {} for business_id {}"
             .format(str(r.party_uuid),
                     str(pending_enrolment.survey_id),
                     str(pending_enrolment.business_id)))
    # Send an enrolment event to the case service
    case_id = pending_enrolment.case_id
    log.info("Pending enrolment for case_id :: " + str(case_id))
    post_case_event(str(case_id), str(r.party_uuid), "RESPONDENT_ENROLED", "Respondent enrolled")
    sess.delete(pending_enrolment)


def register_user(party, tran):
    # TODO: Comments and explanation
    client_id = current_app.config.dependency['oauth2-service']['client_id']
    client_secret = current_app.config.dependency['oauth2-service']['client_secret']

    oauth_payload = {
        "username": party['emailAddress'],
        "password": party['password'],
        "client_id": client_id,
        "client_secret": client_secret
    }
    oauth_svc = current_app.config.dependency['oauth2-service']
    oauth_url = build_url('{}://{}:{}{}', oauth_svc, oauth_svc['admin_endpoint'])
    auth = (client_id, client_secret)
    oauth_response = Requests.post(oauth_url, auth=auth, data=oauth_payload)
    if not oauth_response.status_code == 201:
        log.info("Registering respondent OAuth2 server responded with {} {}"
                 .format(oauth_response.status_code, oauth_response.content))
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
    # TODO: Comments and explanation
    iac_svc = current_app.config.dependency['iac-service']
    iac_url = build_url('{}://{}:{}/iacs/{}', iac_svc, enrolment_code)
    log.info("GET URL {}".format(iac_url))
    response = Requests.get(iac_url)
    log.info("IAC service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_case(enrolment_code):
    # TODO: Comments and explanation
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    log.info("GET URL {}".format(case_url))
    response = Requests.get(case_url)
    log.info("Case service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_collection_exercise(collection_exercise_id):
    # TODO: Comments and explanation
    ce_svc = current_app.config.dependency['collectionexercise-service']
    ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    log.info("GET {}".format(ce_url))
    response = Requests.get(ce_url)
    log.info("Collection exercise service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_survey(survey_id):
    # TODO: Comments and explanation
    survey_svc = current_app.config.dependency['survey-service']
    survey_url = build_url('{}://{}:{}/surveys/{}', survey_svc, survey_id)
    log.info("GET {}".format(survey_url))
    response = Requests.get(survey_url)
    log.info("Survey service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def post_case_event(case_id, party_id, category="Default category message", desc="Default description message"):
    # TODO: Comments and explanation
    # TODO: Consider making this it's own python module in the Flask App. Or having a class for this.

    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/{}/events', case_svc, case_id)
    payload = {
        'description': desc,
        'category': category,
        'partyId': party_id,
        'createdBy': "Party Service"
    }

    log.info("POST {} payload={}".format(case_url, payload))
    response = Requests.post(case_url, json=payload)
    log.info("Case service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


@with_db_session
def _query_respondent_by_party_uuid(party_uuid, session):
    """
    Query to return respondent based on party uuid
    :param party_uuid: the pary uuid
    :return: respondent
    """
    log.debug('Querying respondents with party_uuid {}'.format(party_uuid))

    return session.query(Respondent).filter(Respondent.party_uuid == party_uuid).first()


def resend_verification_email(party_uuid):
    """
    Check and resend an email verification email
    :param party_uuid: the party uuid
    :return: make_response
    """
    log.debug('attempting to resend verification_email with party_uuid {}'.format(party_uuid))

    respondent = _query_respondent_by_party_uuid(party_uuid)

    if not respondent:
        log.debug(NO_RESPONDENT_FOR_PARTY_ID)
        return make_response(NO_RESPONDENT_FOR_PARTY_ID, 404)

    if respondent.status == RespondentStatus.ACTIVE:
        log.debug(EMAIL_ALREADY_VERIFIED)
        return make_response(EMAIL_ALREADY_VERIFIED, 200)

    _send_email_verification(party_uuid, respondent.email_address)

    return make_response(EMAIL_VERIFICATION_SEND, 200)


def _send_email_verification(party_uuid, email):
    """
    Send an email verification to the respondent
    :param email:
    :param party_uuid:
    """

    verification_url = _create_verification_url(email)
    log.info("Verification URL for party_id: {} {}".format(party_uuid, verification_url))

    notify_service = current_app.config.dependency['gov-uk-notify-service']
    template_id = notify_service['gov_notify_template_id']
    _send_message_to_gov_uk_notify(email, template_id, verification_url, party_uuid)


def _create_verification_url(email):
    """
    Create a verification url for an email
    :param email:
    :return: verification_url
    """

    log.info('creating verification url')

    secret_key = current_app.config["SECRET_KEY"]
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"] or 'email-confirm-key'
    timed_serializer = URLSafeTimedSerializer(secret_key)
    token = timed_serializer.dumps(email, salt=email_token_salt)
    public_email_verification_url = current_app.config["PUBLIC_EMAIL_VERIFICATION_URL"]
    verification_url = '{}/register/activate-account/{}'.format(public_email_verification_url, token)

    return verification_url


def _send_message_to_gov_uk_notify(email, template_id, url, party_id):
    """
    Send a message to GOVUK notify
    :param email: respondents email address
    :param template_id:
    :param url:
    :param party_id:
    """

    log.info('sending message to gov uk notify')

    personalisation = {
        'ACCOUNT_VERIFICATION_URL': url
    }

    if current_app.config.feature['send_email_to_gov_notify']:
        log.info("Sending verification email for party_id: {}".format(party_id))
        try:
            notifier = GovUKNotify()
            notifier.send_message(email, template_id, personalisation, party_id)
        except RasNotifyError:
            # Note: intentionally suppresses exception
            log.error("Error sending verification email for party_id {}".format(party_id))
    else:
        log.info("Verification email not sent. Feature send_email_to_gov_notify=false")


@translate_exceptions
@with_db_session
def change_respondent_email(party_uuid, email_address, session):
    respondent = session.query(Respondent).filter(Respondent.party_uuid == party_uuid).first()
    if not respondent:
        return make_response(jsonify({'errors': "Respondent with party id '{}' does not exist.".format(party_uuid)}), 404)

    set_user_unverified(respondent.email_address)

    respondent.email_address = email_address
    respondent.status = RespondentStatus.CREATED

    _send_email_verification(party_uuid, respondent.email_address)

    return make_response(jsonify(respondent.to_respondent_dict()), 200)
