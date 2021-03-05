import logging
import uuid

import structlog
from flask import current_app
from itsdangerous import SignatureExpired, BadSignature, BadData
from requests import HTTPError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, NotFound, UnprocessableEntity

from ras_party.clients.oauth_client import OauthClient
from ras_party.controllers.case_controller import get_cases_for_casegroup, post_case_event
from ras_party.controllers.iac_controller import disable_iac, request_iac
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.queries import count_enrolment_by_survey_business
from ras_party.controllers.queries import query_business_respondent_by_respondent_id_and_business_id
from ras_party.controllers.queries import query_enrolment_by_survey_business_respondent
from ras_party.controllers.queries import query_respondent_by_email, query_respondent_by_pending_email
from ras_party.controllers.queries import query_respondent_by_party_uuid, query_business_by_party_uuid
from ras_party.controllers.queries import query_all_non_disabled_enrolments_respondent
from ras_party.controllers.queries import query_single_respondent_by_email
from ras_party.controllers.validate import Exists, Validator
from ras_party.exceptions import RasNotifyError
from ras_party.models.models import BusinessRespondent, Enrolment, EnrolmentStatus
from ras_party.models.models import PendingEnrolment, Respondent, RespondentStatus
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session, with_query_only_db_session
from ras_party.support.session_decorator import with_quiet_db_session
from ras_party.support.transactional import transactional
from ras_party.support.verification import decode_email_token
from ras_party.support.util import obfuscate_email

logger = structlog.wrap_logger(logging.getLogger(__name__))

NO_RESPONDENT_FOR_PARTY_ID = 'There is no respondent with that party ID'
EMAIL_VERIFICATION_SENT = 'A new verification email has been sent'


# flake8: noqa: C901
@with_quiet_db_session
def post_respondent(party, session):
    """
    Register respondent and set up pending enrolment before account verification
    :param party: respondent to be created details
    :param session
    :return: created respondent
    """

    # Validation, curation and checks
    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'enrolmentCode')

    v = Validator(Exists(*expected))
    if 'id' in party:
        # Note: there's not strictly a requirement to be able to pass in a UUID, this is currently supported to
        # aid with testing.
        logger.info("'id' in respondent post message")
        try:
            uuid.UUID(party['id'])
        except ValueError:
            logger.info("Invalid respondent id type", respondent_id=party['id'])
            raise BadRequest(f"'{party['id']}' is not a valid UUID format for property 'id'")

    if not v.validate(party):
        logger.debug(v.errors)
        raise BadRequest(v.errors)

    iac = request_iac(party['enrolmentCode'])
    if not iac.get('active'):
        logger.info("Inactive enrolment code")
        raise BadRequest("Enrolment code is not active")

    existing = query_respondent_by_email(party['emailAddress'].lower(), session)
    if existing:
        logger.info("Email already exists", party_uuid=str(existing.party_uuid))
        raise BadRequest("Email address already exists")

    case_context = request_case(party['enrolmentCode'])
    case_id = case_context['id']
    business_id = case_context['partyId']
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    collection_exercise = request_collection_exercise(collection_exercise_id)
    survey_id = collection_exercise['surveyId']

    business = query_business_by_party_uuid(business_id, session)
    if not business:
        logger.error("Could not locate business when creating business association",
                     business_id=business_id, case_id=case_id, collection_exercise_id=collection_exercise_id)
        raise InternalServerError("Could not locate business when creating business association")

    # Chain of enrolment processes
    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'].lower(),
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone'],
        'status': RespondentStatus.CREATED
    }

    # This might look odd but it's done in the interest of keeping the code working in the same way.
    # If raise_for_status in the function raises an error, it would've been caught by @with_db_session,
    # rolled back the db and raised it.  Whether that's something we want is another question.
    try:
        respondent = _add_enrolment_and_auth(business, business_id, case_id, party, session, survey_id,
                                             translated_party)
    except HTTPError:
        logger.error("add_enrolment_and_auth raised an HTTPError", exc_info=True)
        session.rollback()
        raise

    # If the disabling of the enrolment code fails we log an error and continue anyway.  In the interest of keeping
    # the code working in the same way (which may itself be wrong...) we'll handle the ValueError that can be raised
    # in the same way as before (rollback the session and raise) but it's not clear whether this is the desired
    # behaviour.
    try:
        disable_iac(party['enrolmentCode'], case_id)
    except ValueError:
        logger.error("disable_iac didn't return json in its response", exc_info=True)
        session.rollback()
        raise

    _send_email_verification(respondent.party_uuid, party['emailAddress'].lower())

    return respondent.to_respondent_dict()


def _add_enrolment_and_auth(business, business_id, case_id, party, session, survey_id, translated_party):
    """Create and persist new party entities and attempt to register with auth service.
    Auth fails lead to party entities being rolled back.
    The context manager commits to sub session.
    If final commit fails an account will be in auth not party, this circumstance is unlikely but possible
    """
    try:
        with session.begin_nested():

            # Use a sub transaction to store party data
            # Context manager will manage commits/rollback

            # Create the enrolment respondent-business-survey associations

            respondent = Respondent(**translated_party)
            business_respondent = BusinessRespondent(business=business, respondent=respondent)
            pending_enrolment = PendingEnrolment(case_id=case_id,
                                                 respondent=respondent,
                                                 business_id=business_id,
                                                 survey_id=survey_id)
            Enrolment(business_respondent=business_respondent,
                      survey_id=survey_id,
                      status=EnrolmentStatus.PENDING)

            session.add(respondent)
            session.add(pending_enrolment)

    except SQLAlchemyError:
        logger.exception('Party service db post respondent caused exception', party_uuid=translated_party['party_uuid'])
        raise  # re raise the exception aimed at the generic handler
    else:
        # Register user to auth server after successful commit
        oauth_response = OauthClient().create_account(party['emailAddress'].lower(), party['password'])
        if not oauth_response.status_code == 201:
            logger.info('Registering respondent auth service responded with', status=oauth_response.status_code,
                        content=oauth_response.content)

            session.rollback()  # Rollback to SAVEPOINT
            oauth_response.raise_for_status()

        session.commit()  # Full session commit

    logger.info("New user has been registered via the auth-service", party_uuid=translated_party['party_uuid'])
    return respondent


@with_db_session
def change_respondent_enrolment_status(payload, session):
    """
    Change respondent enrolment status for respondent and survey. Takes params from a payload dict

    :param payload: A dictionary holding the values for the respondent party id being modified
    """
    respondent_id = payload['respondent_id']

    respondent = query_respondent_by_party_uuid(respondent_id, session)
    if not respondent:
        logger.info("Respondent does not exist", respondent_id=respondent_id)
        raise NotFound("Respondent does not exist")

    return _change_respondent_enrolment_status(respondent=respondent,
                                               survey_id=payload['survey_id'],
                                               business_id=payload['business_id'],
                                               status=payload['change_flag'],
                                               session=session)


def _change_respondent_enrolment_status(respondent, survey_id, business_id, status, session):
    logger.info("Attempting to change respondent enrolment",
                respondent_id=respondent.party_uuid,
                survey_id=survey_id,
                business_id=business_id,
                status=status)

    respondent = query_respondent_by_party_uuid(respondent.party_uuid, session)
    if not respondent:
        logger.info("Respondent does not exist", respondent_id=respondent.party_uuid)
        raise NotFound("Respondent does not exist")

    enrolment = query_enrolment_by_survey_business_respondent(respondent_id=respondent.id,
                                                              business_id=business_id,
                                                              survey_id=survey_id,
                                                              session=session)
    enrolment.status = status
    session.commit()  # Needs to be committed before call to case as that may look up party

    # If no enrolments are remaining for business/survey
    # then send NO_ACTIVE_ENROLMENTS case event
    enrolment_count = count_enrolment_by_survey_business(business_id, survey_id, session)
    if not enrolment_count:
        logger.info("Informing case service of no active enrolments", survey_id=survey_id,
                    business_id=business_id, respondent_id=respondent.party_uuid)
        post_case_event(case_id=get_case_id_for_business_survey(survey_id, business_id),
                        category='NO_ACTIVE_ENROLMENTS',
                        desc='No active enrolments remaining for case')


@with_db_session
def disable_all_respondent_enrolments(respondent_email, session):
    """Disables all enrolments for a respondent ,  returns the count of the removed enrolments"""

    obfuscated_email = obfuscate_email(respondent_email)

    logger.info('Disabling all enrolments for respondent', email=obfuscated_email)

    removed_enrolments_count = 0

    # raises errors if none or multiple, unusual import to avoid circular references
    respondent = get_single_respondent_by_email(respondent_email, session)

    enrolments = query_all_non_disabled_enrolments_respondent(respondent.id, session)

    for enrolment in enrolments:
        _change_respondent_enrolment_status(respondent=respondent,
                                            survey_id=enrolment.survey_id,
                                            business_id=enrolment.business_id,
                                            status='DISABLED',
                                            session=session)
        removed_enrolments_count += 1

    logger.info('Completed disabling respondent enrolments',
                email=obfuscated_email, removed_enrolment_count=removed_enrolments_count)

    return removed_enrolments_count


def get_single_respondent_by_email(email, session):
    """gets a single respondent based on an email address"""
    try:
        respondent = query_single_respondent_by_email(email, session)
    except NoResultFound:
        logger.error("Respondent with email does not exist", email=obfuscate_email(email))
        raise NotFound("Respondent with email does not exist")
    except MultipleResultsFound:
        logger.error("Multiple respondents found for email", email=obfuscate_email(email))
        raise UnprocessableEntity("Multiple users found, unable to proceed")
    logger.info("Found respondent",
                email=obfuscate_email(respondent.email_address),
                party_uuid=respondent.party_uuid,
                id=respondent.id)
    return respondent


@with_db_session
def change_respondent(payload, session):
    """
    Modify an existing respondent's email address, identified by their current email address.
    """
    v = Validator(Exists('email_address', 'new_email_address'))
    if not v.validate(payload):
        logger.info("Payload for change respondent was invalid", errors=v.errors)
        raise BadRequest(v.errors, 400)

    email_address = payload['email_address']
    new_email_address = payload['new_email_address']

    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    if new_email_address == email_address:
        return respondent.to_respondent_dict()

    respondent_with_new_email = query_respondent_by_email(new_email_address, session)
    if respondent_with_new_email:
        logger.info("Respondent with email already exists")
        raise Conflict("New email address already taken")

    respondent.pending_email_address = new_email_address

    # check if respondent has initiated this request
    if 'change_requested_by_respondent' in payload:
        verification_url = PublicWebsite().confirm_account_email_change_url(new_email_address)
        personalisation = {'CONFIRM_EMAIL_URL': verification_url, 'FIRST_NAME': respondent.first_name}
        logger.info('Account change email URL for party_id', party_id=str(respondent.party_uuid), url=verification_url)
        _send_account_email_change_email(personalisation,
                                         template='verify_account_email_change',
                                         email=new_email_address,
                                         party_id=respondent.party_uuid)
    else:
        _send_email_verification(respondent.party_uuid, new_email_address)

    logger.info('Verification email sent for changing respondents email', respondent_id=str(respondent.party_uuid))

    return respondent.to_respondent_dict()


@with_query_only_db_session
def verify_token(token, session):
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        email_address = decode_email_token(token, duration)
    except SignatureExpired:
        logger.info("Expired email verification token")
        raise Conflict("Expired email verification token")
    except (BadSignature, BadData):
        logger.exception("Bad token in verify_token")
        raise NotFound("Unknown email verification token")

    respondent = query_respondent_by_email(email_address, session)
    if not respondent:
        logger.info("Respondent with Email from token does not exist")
        raise NotFound("Respondent does not exist")

    return {'response': "Ok"}


@transactional
@with_db_session
def change_respondent_password(payload, tran, session):
    _is_valid(payload, attribute='new_password')

    respondent = query_respondent_by_email(payload['email_address'], session)
    email_address = respondent.email_address
    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    new_password = payload['new_password']

    # Check and see if the account is active, if not we can now set to active
    if respondent.status != RespondentStatus.ACTIVE:
        # Checking enrolment status, if PENDING we will change it to ENABLED
        logger.info('Checking enrolment status', respondent_id=respondent.party_uuid)
        if respondent.pending_enrolment:
            enrol_respondent_for_survey(respondent, session)

        # We set the party as ACTIVE in this service
        respondent.status = RespondentStatus.ACTIVE
        oauth_response = OauthClient().update_account(
            username=email_address,
            password=new_password,
            account_locked='False')
    else:
        oauth_response = OauthClient().update_account(
            username=email_address,
            password=new_password)

    if oauth_response.status_code != 201:
        logger.error("Unexpected response from auth service, unable to change user password",
                     respondent_id=str(respondent.party_uuid), status=oauth_response.status_code)
        raise InternalServerError("Failed to change respondent password")

    personalisation = {
        'FIRST_NAME': respondent.first_name
    }

    party_id = respondent.party_uuid

    try:
        NotifyGateway(current_app.config).request_to_notify(email=email_address,
                                                            template_name='confirm_password_change',
                                                            personalisation=personalisation,
                                                            reference=str(party_id))
    except RasNotifyError as ras_error:
        logger.error(ras_error)

    # This ensures the log message is only written once the DB transaction is committed
    tran.on_success(lambda: logger.info('Respondent has changed their password', respondent_id=party_id))

    return {'response': "Ok"}


@with_query_only_db_session
def request_password_change(payload, session):
    _is_valid(payload, attribute='email_address')

    logger.info("Verifying user exists before sending password reset email")
    respondent = query_respondent_by_email(payload['email_address'], session)
    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    logger.info("Requesting password change", party_id=respondent.party_uuid)

    email_address = respondent.email_address

    verification_url = PublicWebsite().reset_password_url(email_address)

    personalisation = {
        'RESET_PASSWORD_URL': verification_url,
        'FIRST_NAME': respondent.first_name
    }

    party_id = str(respondent.party_uuid)

    logger.info('Reset password url', url=verification_url, party_id=party_id)

    try:
        NotifyGateway(current_app.config).request_to_notify(email=email_address,
                                                            template_name='request_password_change',
                                                            personalisation=personalisation,
                                                            reference=party_id)
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending request to Notify Gateway', respondent_id=party_id)

    logger.info('Password reset email successfully sent', party_id=party_id)

    return {'response': "Ok"}


@with_query_only_db_session
def resend_password_email_expired_token(token, session):
    """
    Check and resend an email verification email using the expired token
    :param token: the expired token
    :param session: database session
    :return: response
    """
    email_address = decode_email_token(token)
    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    payload = {'email_address': email_address}

    response = request_password_change(payload)
    return response


@with_db_session
def notify_change_account_status(payload, party_id, session):
    status = payload['status_change']

    respondent = query_respondent_by_party_uuid(party_id, session)
    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    email_address = respondent.email_address

    # Unlock respondents account
    if status == 'ACTIVE':
        # Checking enrolment status, if PENDING we will change it to ENABLED
        logger.info('Checking enrolment status', respondent_id=party_id)
        if respondent.pending_enrolment:
            enrol_respondent_for_survey(respondent, session)

        oauth_response = OauthClient().update_account(username=email_address, account_locked='False')
        try:
            oauth_response.raise_for_status()
        except HTTPError:
            logger.error("Unexpected response from auth service, unable to unlock account",
                         respondent_id=str(respondent.party_uuid), status=oauth_response.status_code)
            raise InternalServerError('Failed to unlock respondent account')

        logger.info('Respondent account updated', respondent_id=party_id)

    # Lock and notify respondent of account lock
    elif status == 'SUSPENDED':
        _is_valid(payload, attribute='email_address')
        verification_url = PublicWebsite().reset_password_url(email_address)
        personalisation = {
            'RESET_PASSWORD_URL': verification_url,
            'FIRST_NAME': respondent.first_name
        }
        logger.info('Unlock account via password reset url', url=verification_url, party_id=party_id)

        try:
            NotifyGateway(current_app.config).request_to_notify(email=email_address,
                                                                template_name='notify_account_locked',
                                                                personalisation=personalisation,
                                                                reference=party_id)
        except RasNotifyError:
            # Note: intentionally suppresses exception
            logger.error('Error sending request to Notify Gateway', respondent_id=party_id)

        logger.info('Notification email successfully sent', party_id=party_id)

    respondent.status = status

    return {'response': "Ok"}


@transactional
@with_db_session
def put_email_verification(token, tran, session):
    """
    Verify email address, this method can be reached when registering or updating email address
    :param token:
    :param tran:
    :param session: db session
    :return: Verified respondent details
    """
    logger.info('Attempting to verify email', token=token)
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        email_address = decode_email_token(token, duration)
    except SignatureExpired:
        logger.info("Expired email verification token")
        raise Conflict("Expired email verification token")
    except (BadSignature, BadData):
        logger.exception("Bad token in put_email_verification")
        raise NotFound("Unknown email verification token")

    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        logger.info("Attempting to find respondent by pending email address")
        # When changing contact details, unverified new email is in pending_email_address
        respondent = query_respondent_by_pending_email(email_address, session)

        if respondent:
            # Get old email address
            old_email_address = respondent.email_address
            update_verified_email_address(respondent, tran)
            # send confirmation email to old email address
            personalisation = {
                'FIRST_NAME': respondent.first_name,
                'NEW_EMAIL': respondent.email_address
            }
            logger.info("Sending change of email on account to previously held email address")
            _send_account_email_change_email(personalisation=personalisation,
                                             template='confirm_change_to_account_email',
                                             email=old_email_address,
                                             party_id=respondent.party_uuid)
        else:
            logger.info("Unable to find respondent by pending email")
            raise NotFound("Unable to find user while checking email verification token")

    if respondent.status != RespondentStatus.ACTIVE:
        # We set the party as ACTIVE in this service
        respondent.status = RespondentStatus.ACTIVE

        # Next we check if this respondent has a pending enrolment (there WILL be only one, set during registration)
        if respondent.pending_enrolment:
            enrol_respondent_for_survey(respondent, session)
        else:
            logger.info('No pending enrolment for respondent while checking email verification token',
                        party_uuid=str(respondent.party_uuid))

        # We set the user as verified on the OAuth2 server.
        set_user_verified(email_address)

    return respondent.to_respondent_dict()


def update_verified_email_address(respondent, tran):
    """
    Update the email address in the auth service.

    :param respondent: A respondent object
    :type respondent: Respondent
    :param tran: A transaction session (used to handle rollbacks on failures)
    """
    logger.info('Attempting to update verified email address')

    new_email_address = respondent.pending_email_address
    email_address = respondent.email_address

    oauth_response = OauthClient().update_account(
        username=email_address,
        new_username=new_email_address,
        account_verified='true')

    if oauth_response.status_code != 201:
        logger.error("Unexpected response from auth service, unable to change user email",
                     respondent_id=str(respondent.party_uuid), status=oauth_response.status_code)
        raise InternalServerError("Failed to change respondent email")

    def compensate_oauth_change():
        rollback_response = OauthClient().update_account(
            username=new_email_address,
            new_username=email_address,
            account_verified='true')
        respondent.pending_email_address = new_email_address

        if rollback_response.status_code != 201:
            logger.error("Unexpected response from auth service, unable to rollback change to respondent email",
                         respondent_id=str(respondent.party_uuid), status=oauth_response.status_code)
            raise InternalServerError("Failed to rollback change to respondent email")

    tran.compensate(compensate_oauth_change)

    respondent.email_address = new_email_address
    respondent.pending_email_address = None

    tran.on_success(lambda: logger.info('Updated verified email address'))


@with_query_only_db_session
def resend_verification_email_by_uuid(party_uuid, session):
    """
    Check and resend an email verification email using the party id
    :param party_uuid: the party uuid
    :param session: database session
    :return: response

    """
    logger.info('Attempting to resend verification email', party_uuid=party_uuid)

    respondent = query_respondent_by_party_uuid(party_uuid, session)
    if not respondent:
        logger.info(NO_RESPONDENT_FOR_PARTY_ID, party_uuid=party_uuid)
        raise NotFound(NO_RESPONDENT_FOR_PARTY_ID)

    response = _resend_verification_email(respondent)
    logger.info('Verification email successfully resent', party_uuid=party_uuid)
    return response


@with_query_only_db_session
def resend_account_email_change_verification_email_expired_token(token, session):
    """
    Check and resend an email on account email change when expired token
    :param token: the expired token
    :param session: database session
    :return: response
    """
    logger.info('Attempting to resend account email change email with expired token', token=token)
    email_address = decode_email_token(token)
    respondent = query_respondent_by_pending_email(email_address, session)

    if not respondent:
        logger.info("Respondent does not exist", token=token)
        raise NotFound("Respondent does not exist")

    verification_url = PublicWebsite().confirm_account_email_change_url(email_address)
    personalisation = {'CONFIRM_EMAIL_URL': verification_url, 'FIRST_NAME': respondent.first_name}
    logger.info('Account change email URL for party_id', party_id=str(respondent.party_uuid), url=verification_url)
    _send_account_email_change_email(personalisation,
                                     template='verify_account_email_change',
                                     email=email_address,
                                     party_id=respondent.party_uuid)
    logger.info('Successfully resent account email change verification email', token=token)
    return {'message': EMAIL_VERIFICATION_SENT}


@with_query_only_db_session
def resend_verification_email_expired_token(token, session):
    """
    Check and resend an email verification email using the expired token
    :param token: the expired token
    :param session: database session
    :return: response
    """
    logger.info('Attempting to resend verification email with expired token', token=token)
    email_address = decode_email_token(token)
    respondent = query_respondent_by_email(email_address, session)

    if not respondent:
        logger.info("Respondent does not exist", token=token)
        raise NotFound("Respondent does not exist")

    response = _resend_verification_email(respondent)
    logger.info('Successfully resent verification email with expired token', token=token)
    return response


def _resend_verification_email(respondent):
    if respondent.pending_email_address:
        _send_email_verification(respondent.party_uuid, respondent.pending_email_address)
    else:
        _send_email_verification(respondent.party_uuid, respondent.email_address)

    return {'message': EMAIL_VERIFICATION_SENT}


@transactional
@with_db_session
def add_new_survey_for_respondent(payload, tran, session):
    """
    Add a survey for an existing respondent
    :param payload: json containing party_id and enrolment_code
    :param tran:
    :param session: database session
    """
    logger.info("Enrolling existing respondent in survey")

    respondent_party_id = payload['party_id']
    enrolment_code = payload['enrolment_code']

    iac = request_iac(enrolment_code)
    if not iac.get('active'):
        logger.info("Inactive enrolment code")
        raise BadRequest("Enrolment code is not active")

    respondent = query_respondent_by_party_uuid(respondent_party_id, session)
    case_context = request_case(enrolment_code)
    case_id = case_context['id']
    business_id = case_context['partyId']
    collection_exercise_id = case_context['caseGroup']['collectionExerciseId']
    collection_exercise = request_collection_exercise(collection_exercise_id)
    survey_id = collection_exercise['surveyId']

    business_respondent = query_business_respondent_by_respondent_id_and_business_id(
        business_id, respondent.id, session)

    if not business_respondent:
        # Associate respondent with new business
        business = query_business_by_party_uuid(business_id, session)
        if not business:
            logger.error("Could not find business", business_id=business_id, case_id=case_id,
                         collection_exercise_id=collection_exercise_id)
            raise InternalServerError("Could not locate business when creating business association")
        business_respondent = BusinessRespondent(business=business, respondent=respondent)

    enrolment = Enrolment(business_respondent=business_respondent,
                          survey_id=survey_id,
                          status=EnrolmentStatus.ENABLED)
    session.add(enrolment)
    session.commit()

    disable_iac(enrolment_code, case_id)

    if count_enrolment_by_survey_business(survey_id, business_id, session) == 0:
        logger.info("Informing case of respondent enrolled", survey_id=survey_id, business_id=business_id,
                    respondent_id=respondent.party_uuid)
        post_case_event(case_id=case_id, category="RESPONDENT_ENROLED", desc="Respondent enroled")

    # This ensures the log message is only written once the DB transaction is committed
    tran.on_success(lambda: logger.info('Respondent has enroled to survey for business',
                                        business=business_id))


def _send_email_verification(party_id, email):
    """
    Send an email verification to the respondent
    """
    verification_url = PublicWebsite().activate_account_url(email)
    personalisation = {'ACCOUNT_VERIFICATION_URL': verification_url}
    logger.info('Verification URL for party_id', party_id=str(party_id), url=verification_url)

    try:
        NotifyGateway(current_app.config).request_to_notify(email=email,
                                                            template_name='email_verification',
                                                            personalisation=personalisation,
                                                            reference=str(party_id))
        logger.info('Verification email sent', party_id=str(party_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending verification email for party_id', party_id=str(party_id))


def _send_account_email_change_email(personalisation, template, email, party_id):
    """
    Send an email to confirm changes to respondent account
    """
    try:
        logger.info('sending confirmation email for respondent account change', party_id=str(party_id))
        NotifyGateway(current_app.config).request_to_notify(email=email,
                                                            template_name=template,
                                                            personalisation=personalisation)
        logger.info('confirmation email for respondent account change sent', party_id=str(party_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending verification email for party_id', party_id=str(party_id))


def set_user_verified(email_address):
    """
    Helper function to set the 'verified' flag on the OAuth2 server for a user.
    If it fails a raise_for_status is executed
    """
    logger.info("Setting user active on OAuth2 server")
    oauth_response = OauthClient().update_account(username=email_address, account_verified='true')
    if oauth_response.status_code != 201:
        logger.error("Unable to set the user active on the OAuth2 server")
        oauth_response.raise_for_status()


def enrol_respondent_for_survey(respondent, session):
    """
    Enrol a respondent for a survey

    Searches for a respondent with a matching id in the pending enrolment table.  Once the respondent
    has been enroled, the pending enrolment is deleted

    :param respondent: A Respondent db object
    :param session: A db session
    """

    pending_enrolment_id = respondent.pending_enrolment[0].id
    pending_enrolment = session.query(PendingEnrolment).filter(
        PendingEnrolment.id == pending_enrolment_id).one()
    enrolment = session.query(Enrolment) \
        .filter(Enrolment.business_id == str(pending_enrolment.business_id)) \
        .filter(Enrolment.survey_id == str(pending_enrolment.survey_id)) \
        .filter(Enrolment.respondent_id == respondent.id).one()
    enrolment.status = EnrolmentStatus.ENABLED
    session.add(enrolment)
    logger.info('Enabling pending enrolment for respondent', party_uuid=respondent.party_uuid,
                survey_id=pending_enrolment.survey_id, business_id=pending_enrolment.business_id)

    # Send an enrolment event to the case service
    case_id = pending_enrolment.case_id
    logger.info('Pending enrolment for case_id', case_id=case_id)
    if count_enrolment_by_survey_business(enrolment.business_id, enrolment.survey_id, session) == 0:
        logger.info("Informing case of respondent enrolled", survey_id=enrolment.survey_id,
                    business_id=enrolment.business_id, party_uuid=respondent.party_uuid)
        post_case_event(case_id=case_id, category="RESPONDENT_ENROLED", desc="Respondent enrolled")
    session.delete(pending_enrolment)


def register_user(party):
    """
    Create an account for the user in the auth service
    """
    oauth_response = OauthClient().create_account(party['emailAddress'], party['password'])
    if not oauth_response.status_code == 201:
        logger.info('Registering respondent OAuth2 server responded with', status=oauth_response.status_code,
                    content=oauth_response.content)
        oauth_response.raise_for_status()

    logger.info("New user has been registered via the oauth2-service")


def request_case(enrolment_code):
    """
    Contact the case service to retrieve a case for a given enrolment code

    :param enrolment_code: A respondent provided enrolment code
    """
    case_url = f'{current_app.config["CASE_URL"]}/cases/iac/{enrolment_code}'
    logger.info('Retrieving case from an enrolment code', enrolment_code=enrolment_code)
    response = Requests.get(case_url)
    response.raise_for_status()
    logger.info("Successfully retrieved case from an enrolment code", enrolment_code=enrolment_code)
    return response.json()


def request_collection_exercise(collection_exercise_id):
    """
    Contact the collection exercise service for a collection exercise by id

    :param collection_exercise_id: The id of the collection exercise
    """
    ce_url = f'{current_app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/{collection_exercise_id}'
    logger.info('Retrieving collection exercise by id', collection_exercise_id=collection_exercise_id)
    response = Requests.get(ce_url)
    response.raise_for_status()
    logger.info("Successfully retrived collection exercise by id")
    return response.json()


def request_survey(survey_id):
    """
    Contact the survey service to get the details of a survey from its uuid.

    :param survey_id: A uuid of a survey
    """
    survey_url = f'{current_app.config["SURVEY_URL"]}/surveys/{survey_id}'
    logger.info("Retrieving survey information from the survey service", survey_id=survey_id)
    response = Requests.get(survey_url)
    response.raise_for_status()
    logger.info('Successfully retrieved survey information from the survey service', survey_id=survey_id)
    return response.json()


def request_casegroups_for_business(business_id):
    logger.info('Retrieving casegroups for business', business_id=business_id)
    url = f'{current_app.config["CASE_URL"]}/casegroups/partyid/{business_id}'
    response = Requests.get(url)
    response.raise_for_status()
    logger.info('Successfully retrieved casegroups for business', business_id=business_id)
    return response.json()


def request_collection_exercises_for_survey(survey_id):
    logger.info('Retrieving collection exercises for survey', survey_id=survey_id)
    url = f'{current_app.config["COLLECTION_EXERCISE_URL"]}/collectionexercises/survey/{survey_id}'
    response = Requests.get(url)
    response.raise_for_status()
    logger.info('Successfully retrieved collection exercises for survey', survey_id=survey_id)
    return response.json()


def get_business_survey_casegroups(survey_id, business_id):
    logger.info('Retrieving casegroups for business and survey', survey_id=survey_id, business_id=business_id)
    collection_exercise_ids = [ce['id']
                               for ce in request_collection_exercises_for_survey(survey_id)]
    casegroups = request_casegroups_for_business(business_id)

    # Filtering casegroups by collection exercise ids
    ce_casegroup_ids = [casegroup['id'] for casegroup in casegroups
                        if casegroup['collectionExerciseId'] in collection_exercise_ids]
    logger.info('Successfully retrieved casegroups for business and survey',
                survey_id=survey_id, business_id=business_id)
    return ce_casegroup_ids


def get_case_id_for_business_survey(survey_id, business_id):
    logger.info('Retrieving case for survey and business', survey_id=survey_id, business_id=business_id)

    case_group_ids = get_business_survey_casegroups(survey_id, business_id)
    cases = get_cases_for_casegroup(case_group_ids[0])

    return cases[0]['id']


def _is_valid(payload, attribute):
    v = Validator(Exists(attribute))
    if v.validate(payload):
        return True
    logger.debug(v.errors)
    raise BadRequest(v.errors, 400)
