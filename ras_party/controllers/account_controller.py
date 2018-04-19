import logging
import uuid

from flask import current_app
from itsdangerous import SignatureExpired, BadSignature, BadData
from sqlalchemy import orm
import structlog

from ras_party.clients.oauth_client import OauthClient
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.queries import query_respondent_by_email, query_respondent_by_pending_email
from ras_party.controllers.queries import query_respondent_by_party_uuid, query_business_by_party_uuid
from ras_party.controllers.queries import query_business_respondent_by_respondent_id_and_business_id
from ras_party.controllers.queries import query_enrolment_by_survey_business_respondent
from ras_party.controllers.validate import Exists, IsUuid, Validator
from ras_party.exceptions import RasError, RasNotifyError
from ras_party.models.models import BusinessRespondent, Enrolment, EnrolmentStatus
from ras_party.models.models import PendingEnrolment, Respondent, RespondentStatus
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.transactional import transactional
from ras_party.support.verification import decode_email_token

logger = structlog.wrap_logger(logging.getLogger(__name__))

NO_RESPONDENT_FOR_PARTY_ID = 'There is no respondent with that party ID '
EMAIL_VERIFICATION_SENT = 'A new verification email has been sent'


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

    # Validation, curation and checks
    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        # Note: there's not strictly a requirement to be able to pass in a UUID, this is currently supported to
        # aid with testing.
        logger.debug("'id' in respondent post message. Adding validation rule IsUuid")
        v.add_rule(IsUuid('id'))

    if not v.validate(party):
        raise RasError(v.errors, 400)

    iac = request_iac(party['enrolmentCode'])
    if not iac.get('active'):
        raise RasError("Enrolment code is not active.", status=400)

    existing = query_respondent_by_email(party['emailAddress'], session)
    if existing:
        raise RasError("Email address already exists.", status=400, party_uuid=party.get('party_uuid', None))

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
        raise RasError("There is no survey bound for this user", party_uuid=party['party_uuid'])

    business = query_business_by_party_uuid(business_id, session)
    if not business:
        raise RasError("Could not locate business when creating business association", business_id=business_id,
                       status=404)

    # Chain of enrolment processes
    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'],
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone'],
        'status': RespondentStatus.CREATED
    }

    try:
        #  Create the enrolment respondent-business-survey associations
        respondent = Respondent(**translated_party)
        br = BusinessRespondent(business=business, respondent=respondent)
        pending_enrolment = PendingEnrolment(case_id=case_id,
                                             respondent=respondent,
                                             business_id=business_id,
                                             survey_id=survey_id)
        Enrolment(business_respondent=br,
                  survey_id=survey_id,
                  survey_name=survey_name,
                  status=EnrolmentStatus.PENDING)
        session.add(respondent)
        session.add(pending_enrolment)

        # Notify the case service of this account being created
        post_case_event(case_id,
                        respondent.party_uuid,
                        "RESPONDENT_ACCOUNT_CREATED",
                        "New respondent account created")

        _send_email_verification(respondent.party_uuid, party['emailAddress'])
    except (orm.exc.ObjectDeletedError, orm.exc.FlushError, orm.exc.StaleDataError, orm.exc.DetachedInstanceError):
        logger.error('Error updating database for user', party_id=party['id'])
        raise RasError("Error updating database for user", status=500, party_id=party['id'])
    except KeyError:
        logger.error('Missing config keys during enrolment')
        raise RasError('Missing config keys during enrolment', status=500)
    except Exception:
        logger.exeption('Error during enrolment process')
        raise RasError("Error during enrolment process", status=500)

    register_user(party, tran)

    return respondent.to_respondent_dict()


@with_db_session
def change_respondent_enrolment_status(payload, session):
    """
    Change respondent enrolment status for business and survey
    :param payload:
    :param session:
    :return:
    """
    change_flag = payload['change_flag']
    business_id = payload['business_id']
    survey_id = payload['survey_id']
    respondent_id = payload['respondent_id']
    logger.info("Attempting to change respondent enrolment",
                respondent_id=respondent_id,
                survey_id=survey_id,
                business_id=business_id,
                status=change_flag)
    respondent = query_respondent_by_party_uuid(respondent_id, session)
    if not respondent:
        raise RasError("Respondent does not exist.", status=404)

    enrolment = query_enrolment_by_survey_business_respondent(respondent_id=respondent.id,
                                                              business_id=business_id,
                                                              survey_id=survey_id,
                                                              session=session)
    enrolment.status = change_flag

    category = 'DISABLE_RESPONDENT_ENROLMENT' if change_flag == 'DISABLED' else 'ENABLE_RESPONDENT_ENROLMENT'
    description = "Disable respondent enrolment" if change_flag == 'DISABLED' else 'Enable respondent enrolment'
    for case in get_cases_for_collection_exercise(survey_id, business_id, respondent_id):
        post_case_event(case['id'], business_id, category=category, desc=description)


@transactional
@with_db_session
def change_respondent(payload, session):
    """
    Modify an existing respondent's email address, identified by their current email address.
    """
    v = Validator(Exists('email_address', 'new_email_address'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    email_address = payload['email_address']
    new_email_address = payload['new_email_address']

    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        raise RasError("Respondent does not exist.", status=404)

    if new_email_address == email_address:
        return respondent.to_respondent_dict()

    respondent_with_new_email = query_respondent_by_email(new_email_address, session)
    if respondent_with_new_email:
        raise RasError("New email address already taken.", status=409)

    respondent.pending_email_address = new_email_address

    _send_email_verification(respondent.party_uuid, respondent.email_address)

    logger.info('Verification email sent for changing respondents email', party_uuid=respondent.party_uuid)

    return respondent.to_respondent_dict()


@with_db_session
def verify_token(token, session):
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        email_address = decode_email_token(token, duration)
    except SignatureExpired:
        raise RasError('Expired email verification token', status=409, token=token)
    except (BadSignature, BadData) as e:
        raise RasError('Unknown email verification token', status=404, token=token, error=e)

    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        logger.info("Attempting to find respondent by pending email address")
        # When changing contact details, unverified new email is in pending_email_address
        respondent = query_respondent_by_pending_email(email_address, session)

        if respondent:
            update_verified_email_address(respondent)
        else:
            raise RasError("Respondent does not exist.", status=404)

    return {'response': "Ok"}


@transactional
@with_db_session
def update_verified_email_address(respondent, tran, session):

    logger.info('Attempting to update verified email address')

    new_email_address = respondent.pending_email_address
    email_address = respondent.email_address

    oauth_response = OauthClient().update_account(
                                                username=email_address,
                                                new_username=new_email_address,
                                                account_verified='true')

    if oauth_response.status_code != 201:
        raise RasError("Failed to change respondent email")

    def compensate_oauth_change():
        rollback_response = OauthClient().update_account(
                                                        username=new_email_address,
                                                        new_username=email_address,
                                                        account_verified='true')
        respondent.pending_email_address = new_email_address

        if rollback_response.status_code != 201:
            logger.error("Failed to rollback change to respondent email. Please investigate.",
                         party_id=respondent.party_uuid)
            raise RasError("Failed to rollback change to respondent email.")

    tran.compensate(compensate_oauth_change)

    respondent.pending_email_address = None

    tran.on_success(lambda: logger.info('Updated verified email address'))


@transactional
@with_db_session
def change_respondent_password(token, payload, tran, session):
    v = Validator(Exists('new_password'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        email_address = decode_email_token(token, duration)
    except SignatureExpired:
        raise RasError('Expired email verification token', status=409, token=token)
    except (BadSignature, BadData) as e:
        raise RasError('Unknown email verification token', status=404, token=token, error=e)

    respondent = query_respondent_by_email(email_address, session)
    if not respondent:
        raise RasError("Respondent does not exist.", status=404)

    new_password = payload['new_password']

    oauth_response = OauthClient().update_account(
                                                username=email_address,
                                                password=new_password,
                                                account_verified='true')

    if oauth_response.status_code != 201:
        raise RasError("Failed to change respondent password.")

    personalisation = {
        'FIRST_NAME': respondent.first_name
    }

    party_id = respondent.party_uuid

    try:
        NotifyGateway(current_app.config).confirm_password_change(
            email_address, personalisation, str(party_id))
    except RasNotifyError:
        logger.error('Error sending notification email', party_id=party_id)

    # This ensures the log message is only written once the DB transaction is committed
    tran.on_success(lambda: logger.info('Respondent has changed their password', party_id=party_id))

    return {'response': "Ok"}


@with_db_session
def request_password_change(payload, session):
    v = Validator(Exists('email_address'))
    if not v.validate(payload):
        raise RasError(v.errors, 400)

    email_address = payload['email_address']

    respondent = query_respondent_by_email(email_address, session)
    if not respondent:
        raise RasError("Respondent does not exist.", status=404)

    email_address = respondent.email_address
    verification_url = PublicWebsite().reset_password_url(email_address)

    personalisation = {
        'RESET_PASSWORD_URL': verification_url,
        'FIRST_NAME': respondent.first_name
    }

    logger.info('Reset password url', url=verification_url)

    party_id = respondent.party_uuid
    try:
        NotifyGateway(current_app.config).request_password_change(
            email_address, personalisation, str(party_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending notification email for party_id', party_id=party_id)

    return {'response': "Ok"}


@with_db_session
def change_respondent_account_status(payload, party_id, session):

    status = payload['status_change']

    respondent = query_respondent_by_party_uuid(party_id, session)
    if not respondent:
        raise RasError("Unable to find respondent account", status=404)
    respondent.status = status


@with_db_session
def put_email_verification(token, session):
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        email_address = decode_email_token(token, duration)
    except SignatureExpired:
        raise RasError('Expired email verification token', status=409, token=token)
    except (BadSignature, BadData) as e:
        raise RasError('Bad email verification token', status=404, token=token, error=e)

    r = query_respondent_by_email(email_address, session)
    if not r:
        raise RasError("Unable to find user while checking email verification token", status=404)

    if r.status != RespondentStatus.ACTIVE:
        # We set the party as ACTIVE in this service
        r.status = RespondentStatus.ACTIVE

        # Next we check if this respondent has a pending enrolment (there WILL be only one, set during registration)
        if r.pending_enrolment:
            enrol_respondent_for_survey(r, session)
        else:
            logger.info('No pending enrolment for respondent while checking email verification token',
                        party_uuid=r.party_uuid)

    # We set the user as verified on the OAuth2 server.
    set_user_verified(email_address)
    return r.to_respondent_dict()


@with_db_session
def resend_verification_email(party_uuid, session):
    """
    Check and resend an email verification email
    :param party_uuid: the party uuid
    :return: make_response
    """
    logger.debug('Attempting to resend verification_email', party_uuid=party_uuid)

    respondent = query_respondent_by_party_uuid(party_uuid, session)
    if not respondent:
        raise RasError(NO_RESPONDENT_FOR_PARTY_ID, status=404)

    _send_email_verification(party_uuid, respondent.email_address)

    return {'message': EMAIL_VERIFICATION_SENT}


@transactional
@with_db_session
def add_new_survey_for_respondent(payload, tran, session):
    """
    Add a survey for an existing respondent
    :param payload: json containing party_id and enrolment_code
    :param session: database session
    """
    logger.info("Enrolling existing respondent in survey")

    respondent_party_id = payload['party_id']
    enrolment_code = payload['enrolment_code']

    iac = request_iac(enrolment_code)
    if not iac.get('active'):
        raise RasError("Enrolment code is not active.", status=400)

    respondent = query_respondent_by_party_uuid(respondent_party_id, session)

    case_context = request_case(enrolment_code)
    case_id = case_context['id']
    business_id = case_context['partyId']
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    collection_exercise = request_collection_exercise(collection_exercise_id)

    survey_id = collection_exercise['surveyId']
    survey = request_survey(survey_id)
    survey_name = survey['longName']

    br = query_business_respondent_by_respondent_id_and_business_id(business_id, respondent.id, session)

    if not br:
        """
        Associate respondent with new business
        """
        business = query_business_by_party_uuid(business_id, session)
        if not business:
            raise RasError("Could not locate business when creating business association.",
                           business_id=business_id,
                           status=404)
        br = BusinessRespondent(business=business, respondent=respondent)

    enrolment = Enrolment(business_respondent=br,
                          survey_id=survey_id,
                          survey_name=survey_name,
                          status=EnrolmentStatus.ENABLED)
    session.add(enrolment)

    post_case_event(str(case_id), str(respondent_party_id), "RESPONDENT_ENROLED", "Respondent enroled")

    # This ensures the log message is only written once the DB transaction is committed
    tran.on_success(lambda: logger.info('Respondent has enroled to survey for business',
                                        survey_name=survey_name,
                                        business=business_id))


def _send_email_verification(party_id, email):
    """
    Send an email verification to the respondent
    """
    verification_url = PublicWebsite().activate_account_url(email)
    logger.info('Verification URL for party_id', party_id=party_id, url=verification_url)

    personalisation = {
        'ACCOUNT_VERIFICATION_URL': verification_url
    }

    try:
        NotifyGateway(current_app.config).verify_email(email, personalisation, str(party_id))
        logger.info('Verification email sent', party_id=party_id)
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending verification email for party_id', party_id=party_id)


def set_user_verified(email_address):
    """
    Helper function to set the 'verified' flag on the OAuth2 server for a user.
    If it fails a raise_for_status is executed
    """
    logger.info("Setting user active on OAuth2 server")
    oauth_response = OauthClient().update_account(
        username=email_address, account_verified='true')
    if oauth_response.status_code != 201:
        logger.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()


def enrol_respondent_for_survey(r, sess):
    pending_enrolment_id = r.pending_enrolment[0].id
    pending_enrolment = sess.query(PendingEnrolment).filter(
        PendingEnrolment.id == pending_enrolment_id).one()
    enrolment = sess.query(Enrolment) \
        .filter(Enrolment.business_id == str(pending_enrolment.business_id)) \
        .filter(Enrolment.survey_id == str(pending_enrolment.survey_id)) \
        .filter(Enrolment.respondent_id == r.id).one()
    enrolment.status = EnrolmentStatus.ENABLED
    sess.add(enrolment)
    logger.info('Enabling pending enrolment for respondent', party_uuid=r.party_uuid,
                survey_id=pending_enrolment.survey_id, business_id=pending_enrolment.business_id)
    # Send an enrolment event to the case service
    case_id = pending_enrolment.case_id
    logger.info('Pending enrolment for case_id', case_id=case_id)
    post_case_event(str(case_id), str(r.party_uuid), "RESPONDENT_ENROLED", "Respondent enrolled")
    sess.delete(pending_enrolment)


def register_user(party, tran):
    oauth_response = OauthClient().create_account(
        party['emailAddress'], party['password'])
    if not oauth_response.status_code == 201:
        logger.info('Registering respondent OAuth2 server responded with', status=oauth_response.status_code,
                    content=oauth_response.content)
        oauth_response.raise_for_status()

    def dummy_compensating_action():
        # TODO: Undo the user registration.

        logger.info("Placeholder for deleting the user from oauth server")

    # Add a compensating action to try and avoid an exception leaving the user in an invalid state.
    tran.compensate(dummy_compensating_action)
    logger.info("New user has been registered via the oauth2-service")


def request_iac(enrolment_code):
    # TODO: factor out commonality from these request_* functions
    # TODO: Comments and expladummy_compensating_actionnation
    iac_svc = current_app.config['RAS_IAC_SERVICE']
    iac_url = f'{iac_svc}/iacs/{enrolment_code}'
    logger.info('GET URL', url=iac_url)
    response = Requests.get(iac_url)
    logger.info('IAC service responded with', code=response.status_code)
    response.raise_for_status()
    return response.json()


def request_case(enrolment_code):
    case_svc = current_app.config['RAS_CASE_SERVICE']
    case_url = f'{case_svc}/cases/iac/{enrolment_code}'
    logger.info('GET URL', url=case_url)
    response = Requests.get(case_url)
    logger.info('Case service responded with', status=response.status_code)
    response.raise_for_status()
    return response.json()


def request_collection_exercise(collection_exercise_id):
    ce_svc = current_app.config['RAS_COLLEX_SERVICE']
    ce_url = f'{ce_svc}/collectionexercises/{collection_exercise_id}'
    logger.info('GET', url=ce_url)
    response = Requests.get(ce_url)
    logger.info('Collection exercise service responded with', status=response.status_code)
    response.raise_for_status()
    return response.json()


def request_survey(survey_id):
    survey_svc = current_app.config['RAS_SURVEY_SERVICE']
    survey_url = f'{survey_svc}/surveys/{survey_id}'
    logger.info('GET', url=survey_url)
    response = Requests.get(survey_url)
    logger.info('Survey service responded with', status=response.status_code)
    response.raise_for_status()
    return response.json()


def post_case_event(case_id, party_id, category='Default category message', desc='Default description message'):
    logger.debug('Posting case event', case_id=case_id, party_id=party_id)
    case_svc = current_app.config['RAS_CASE_SERVICE']
    case_url = f'{case_svc}/cases/{case_id}/events'
    payload = {
        'description': desc,
        'category': category,
        'partyId': party_id,
        'createdBy': 'Party Service'
    }

    response = Requests.post(case_url, json=payload)
    response.raise_for_status()
    logger.debug('Successfully posted case event')
    return response.json()


def request_cases_for_respondent(respondent_id):
    logger.debug('Retrieving cases for respondent', respondent_id=respondent_id)
    url = f'{current_app.config["RAS_CASE_SERVICE"]}/cases/partyid/{respondent_id}'
    response = Requests.get(url)
    response.raise_for_status()
    logger.debug('Successfully retrieved cases for respondent', respondent_id=respondent_id)
    return response.json()


def request_casegroups_for_business(business_id):
    logger.debug('Retrieving casegroups for business', business_id=business_id)
    url = f'{current_app.config["RAS_CASE_SERVICE"]}/casegroups/partyid/{business_id}'
    response = Requests.get(url)
    response.raise_for_status()
    logger.debug('Successfully retrieved casegroups for business', business_id=business_id)
    return response.json()


def request_collection_exercises_for_survey(survey_id):
    logger.debug('Retrieving collection exercises for survey', survey_id=survey_id)
    url = f'{current_app.config["RAS_COLLEX_SERVICE"]}/collectionexercises/survey/{survey_id}'
    response = Requests.get(url)
    response.raise_for_status()
    logger.debug('Successfully retrieved collection exercises for survey', survey_id=survey_id)
    return response.json()


def get_cases_for_collection_exercise(survey_id, business_id, respondent_id):
    logger.debug('Retrieving cases for collection exercises',
                 survey_id=survey_id, business_id=business_id, respondent_id=respondent_id)
    collection_exercises = request_collection_exercises_for_survey(survey_id)
    casegroups = request_casegroups_for_business(business_id)
    cases = request_cases_for_respondent(respondent_id)

    ce_casegroups = [casegroup for casegroup in casegroups
                     if casegroup['collectionExerciseId'] in
                     [collection_exercise['id'] for collection_exercise in collection_exercises]]

    matching_cases = [case for case in cases
                      if case['caseGroup']['id'] in
                      [casegroup['id'] for casegroup in ce_casegroups]]
    logger.debug('Successfully retrieved cases for collection exercises',
                 survey_id=survey_id, business_id=business_id, respondent_id=respondent_id)
    return matching_cases
