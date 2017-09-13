import uuid

from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature, BadData
from ras_common_utils.ras_error.ras_error import RasError, RasNotifyError
from sqlalchemy import orm
from structlog import get_logger

from ras_party.clients.oauth_client import OauthClient
from ras_party.controllers.error_decorator import translate_exceptions
from ras_party.controllers.gov_uk_notify import GovUKNotify
from ras_party.controllers.validate import Validator, IsUuid, IsIn, Exists, MutuallyExclusive
from ras_party.models.models import Business, Respondent, RespondentStatus, BusinessRespondent, PendingEnrolment, \
    Enrolment, EnrolmentStatus
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.transactional import transactional
from ras_party.support.util import build_url

log = get_logger()

NO_RESPONDENT_FOR_PARTY_ID = 'There is no respondent with that party ID '
EMAIL_ALREADY_VERIFIED = 'The Respondent for that party ID is already verified'
EMAIL_VERIFICATION_SENT = 'A new verification email has been sent'


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
        raise RasError("Business with reference '{}' does not exist.".format(ref), status_code=404)

    return business.to_business_dict()


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
        raise RasError(v.errors, status_code=400)

    business = session.query(Business).filter(Business.party_uuid == id).first()
    if not business:
        raise RasError("Business with party id '{}' does not exist.".format(id), status_code=404)

    return business.to_business_dict()


@translate_exceptions
@with_db_session
def businesses_post(business_data, session):
    """
    Create a new business in the database based on the supplied data dictionary.

    :param business_data: dictionary containing the attributes of the business.
    :param session: database session.
    :return: Jsonified representation of the created business.
    """
    party_data = Business.to_party(business_data)

    # FIXME: this is incorrect, it doesn't make sense to require sampleUnitType for the concrete endpoints
    errors = Business.validate(party_data, current_app.config['PARTY_SCHEMA'])
    if errors:
        raise RasError(errors, status_code=400)

    existing_business = session.query(Business).filter(Business.business_ref == party_data['sampleUnitRef']).first()
    if existing_business:
        party_data['id'] = str(existing_business.party_uuid)

    b = Business.from_party_dict(party_data)
    session.merge(b)
    return b.to_business_dict()


@translate_exceptions
@with_db_session
def parties_post(party_data, session):
    """
    Post a new party (with sampleUnitType B)

    :param party_data: packet containing the data to post
    :type party_data: JSON data maching the schema described in schemas/party_schema.json
    :param party_format_response: The format we output on completion
    :type bool: Structured or Flat
    """
    errors = Business.validate(party_data, current_app.config['PARTY_SCHEMA'])
    if errors:
        raise RasError(errors, status_code=400)

    if party_data['sampleUnitType'] != Business.UNIT_TYPE:
        raise RasError([{'message': 'sampleUnitType must be of type ({})'.format(Business.UNIT_TYPE)}], status_code=400)

    existing_business = session.query(Business).filter(Business.business_ref == party_data['sampleUnitRef']).first()
    if existing_business:
        party_data['id'] = str(existing_business.party_uuid)

    b = Business.from_party_dict(party_data)
    session.merge(b)
    return b.to_party_dict()


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
        raise RasError(v.errors, status_code=400)

    business = session.query(Business).filter(Business.business_ref == sample_unit_ref).first()
    if not business:
        raise RasError("Business with reference '{}' does not exist.".format(sample_unit_ref), status_code=404)

    return business.to_party_dict()


@translate_exceptions
@with_db_session
def get_party_by_id(sample_unit_type, id, session):
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sample_unit_type}):
        raise RasError(v.errors, status_code=400)

    if sample_unit_type == Business.UNIT_TYPE:
        business = session.query(Business).filter(Business.party_uuid == id).first()
        if not business:
            raise RasError("Business with id '{}' does not exist.".format(id), status_code=404)

        return business.to_party_dict()

    elif sample_unit_type == Respondent.UNIT_TYPE:
        respondent = session.query(Respondent).filter(Respondent.party_uuid == id).first()
        if not respondent:
            return RasError("Respondent with id '{}' does not exist.".format(id), status_code=404)

        return respondent.to_party_dict()


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
        raise RasError(v.errors, status_code=400)

    respondent = session.query(Respondent).filter(Respondent.party_uuid == id).first()
    if not respondent:
        raise RasError("Respondent with party id '{}' does not exist.".format(id), status_code=404)

    return respondent.to_respondent_dict()


@translate_exceptions
@with_db_session
def get_respondent_by_email(email, session):
    """
    Get a respondent by its email address.
    Returns either the unique respondent identified by the supplied email address, or otherwise raises
    a RasError to indicate the email address doesn't exist.

    :param email: Email of respondent to lookup
    :rtype: Respondent
    """
    respondent = session.query(Respondent).filter(Respondent.email_address == email).one()
    if not respondent:
        raise RasError("Respondent does not exist.", status_code=404)

    return respondent.to_respondent_dict()


@translate_exceptions
@with_db_session
def put_respondent_by_email(payload, session):

    v = Validator(Exists('email_address'), MutuallyExclusive('email_address', 'password'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    email_address = payload['email_address']

    respondent = session.query(Respondent).filter(Respondent.email_address == email_address).one()
    if not respondent:
        raise RasError("Respondent does not exist.", status_code=404)

    respondent.first_name = payload.get('first_name', respondent.first_name)
    respondent.last_name = payload.get('last_name', respondent.last_name)
    respondent.telephone = payload.get('telephone', respondent.telephone)
    respondent.email_address = payload.get('new_email_address', respondent.email_address)

    if 'new_email_address' in payload and email_address != payload['new_email_address']:
        oauth_response = OauthClient(current_app.config).update_account(username=email_address,
                                                                        new_email_address=payload['new_email_address'],
                                                                        account_verified=False)

        # TODO: compensation
        if oauth_response.status_code != 201:
            raise RasError("Failed to change respondent email")

        _send_email_verification(respondent.party_uuid, respondent.email_address)
    elif 'password' in payload:
        oauth_response = OauthClient(current_app.config).update_account(username=email_address,
                                                                        password=payload['password'])

        # TODO: compensation
        if oauth_response.status_code != 201:
            raise RasError("Failed to change respondent password.")

    return respondent.to_respondent_dict()


@translate_exceptions
@with_db_session
def reset_respondent_password_by_email(email, session):
    respondent = session.query(Respondent).filter(Respondent.email_address == email).one()
    if not respondent:
        raise RasError("Respondent does not exist.", status_code=404)


@translate_exceptions
@transactional
@with_db_session
def post_respondent(party, tran, session):
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
        log.debug("'id' in respondent post message. Adding validation rule IsUuid")
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

    return r.to_respondent_dict()


@translate_exceptions
@with_db_session
def put_email_verification(token, session):
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
        return r.to_respondent_dict()

    # We set the party as ACTIVE in this service
    r.status = RespondentStatus.ACTIVE

    # Next we check if this respondent has a pending enrolment (there WILL be only one, set during registration)
    if r.pending_enrolment:
        enrol_respondent_for_survey(r, session)
    else:
        log.info("No pending enrolment for respondent {} while checking email verification token"
                 .format(str(r.party_uuid)))

    # We set the user as verified on the OAuth2 server.
    set_user_verified(email_address)
    return r.to_respondent_dict()


def set_user_verified(email_address):
    """ Helper function to set the 'verified' flag on the OAuth2 server for a user.
        If it fails a raise_for_status is executed
    """
    log.info("Setting user active on OAuth2 server")
    oauth_response = OauthClient(current_app.config).update_account(username=email_address, account_verified=True)
    if oauth_response.status_code != 201:
        log.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()


def enrol_respondent_for_survey(r, sess):
    pending_enrolment_id = r.pending_enrolment[0].id
    pending_enrolment = sess.query(PendingEnrolment).filter(PendingEnrolment.id == pending_enrolment_id).one()
    enrolment = sess.query(Enrolment) \
        .filter(Enrolment.business_id == str(pending_enrolment.business_id)) \
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
    oauth_response = OauthClient(current_app.config).create_account(party['emailAddress'], party['password'])
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
    case_svc = current_app.config.dependency['case-service']
    case_url = build_url('{}://{}:{}/cases/iac/{}', case_svc, enrolment_code)
    log.info("GET URL {}".format(case_url))
    response = Requests.get(case_url)
    log.info("Case service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_collection_exercise(collection_exercise_id):
    ce_svc = current_app.config.dependency['collectionexercise-service']
    ce_url = build_url('{}://{}:{}/collectionexercises/{}', ce_svc, collection_exercise_id)
    log.info("GET {}".format(ce_url))
    response = Requests.get(ce_url)
    log.info("Collection exercise service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def request_survey(survey_id):
    survey_svc = current_app.config.dependency['survey-service']
    survey_url = build_url('{}://{}:{}/surveys/{}', survey_svc, survey_id)
    log.info("GET {}".format(survey_url))
    response = Requests.get(survey_url)
    log.info("Survey service responded with {}".format(response.status_code))
    response.raise_for_status()
    return response.json()


def post_case_event(case_id, party_id, category="Default category message", desc="Default description message"):
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
        raise RasError(NO_RESPONDENT_FOR_PARTY_ID, status_code=404)

    if respondent.status == RespondentStatus.ACTIVE:
        log.debug(EMAIL_ALREADY_VERIFIED)
        return EMAIL_ALREADY_VERIFIED

    _send_email_verification(party_uuid, respondent.email_address)

    return {'message': EMAIL_VERIFICATION_SENT}


def _send_email_verification(party_uuid, email):
    """
    Send an email verification to the respondent
    :param email:
    :param party_uuid:
    """
    verification_url = _create_verification_url(email)
    log.info("Verification URL for party_id: {} {}".format(party_uuid, verification_url))

    notify_service = current_app.config.dependency['notify-service']
    template_id = notify_service['email_verification_template']
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
    public_website = current_app.config.dependency['public-website']
    scheme, host = public_website['scheme'], public_website['host']
    return '{}://{}/register/activate-account/{}'.format(scheme, host, token)


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
            notifier.send_message(email, template_id, personalisation, str(party_id))
        except RasNotifyError:
            # Note: intentionally suppresses exception
            log.error("Error sending verification email for party_id {}".format(party_id))
    else:
        log.info("Verification email not sent. Feature send_email_to_gov_notify=false")
