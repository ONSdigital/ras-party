import logging
import uuid
from datetime import datetime, timedelta
from urllib.error import HTTPError

import structlog
from flask import current_app
from itsdangerous import SignatureExpired, BadSignature, BadData
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Conflict, NotFound, InternalServerError, BadRequest

from ras_party.clients.oauth_client import OauthClient
from ras_party.controllers.account_controller import set_user_verified, get_single_respondent_by_email
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.queries import query_enrolment_by_business_and_survey_and_status, \
    query_pending_surveys_by_business_and_survey, query_pending_survey_by_batch_no, query_business_by_party_uuid, \
    query_respondent_by_party_uuid, query_business_respondent_by_respondent_id_and_business_id, \
    delete_pending_survey_by_batch_no
from ras_party.controllers.respondent_controller import get_respondent_by_email, get_respondent_by_id
from ras_party.controllers.validate import Validator, Exists
from ras_party.models.models import PendingSurveys, BusinessRespondent, Enrolment, EnrolmentStatus, RespondentStatus, \
    Respondent
from ras_party.support.session_decorator import with_query_only_db_session, with_db_session, with_quiet_db_session
from ras_party.support.verification import decode_email_token

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def get_users_enrolled_and_pending_survey_against_business_and_survey(business_id, survey_id, is_transfer, session):
    """
    Get total users count who are already enrolled and pending share survey against business id and survey id
    Returns total user count
    :param business_id: business party id
    :type business_id: str
    :param survey_id: survey id
    :type survey_id: str
    :param is_transfer: if the request is to transfer share
    :type is_transfer: bool
    :param session: db session
    :rtype: int
    """
    bound_logger = logger.bind(business_id=business_id, survey_id=survey_id)
    bound_logger.info('Attempting to get enrolled users')
    enrolled_users = query_enrolment_by_business_and_survey_and_status(business_id, survey_id, session)
    bound_logger.info('Attempting to get pending survey users')
    pending_survey_users = query_pending_surveys_by_business_and_survey(business_id, survey_id, session, is_transfer)
    total_users = enrolled_users.count() + pending_survey_users.count()
    bound_logger.info(f'total users count {total_users}')
    return total_users


@with_db_session
def pending_survey_create(business_id, survey_id, email_address, shared_by, batch_number, is_transfer, session):
    """
    creates a new record for pending survey
    Returns void
    :param business_id: business party id
    :type business_id: str
    :param survey_id: survey id
    :type survey_id: str
    :param email_address: email_address
    :type email_address: str
    :param shared_by: respondent_party_uuid
    :type shared_by: uuid
    :param session: db session
    :param batch_number: batch_number
    :type batch_number: uuid
    :param is_transfer: True if the record is to transfer survey
    :type is_transfer: bool
    :rtype: void
    """
    pending_share = PendingSurveys(business_id=business_id, survey_id=survey_id, email_address=email_address,
                                   shared_by=shared_by, batch_no=batch_number, is_transfer=is_transfer)
    session.add(pending_share)


@with_db_session
def delete_pending_surveys(session):
    """
    Deletes all the existing pending surveys which have expired
    :param session A db session
    """
    _expired_hrs = datetime.utcnow() - timedelta(seconds=float(current_app.config["EMAIL_TOKEN_EXPIRY"]))
    pending_shares = session.query(PendingSurveys).filter(PendingSurveys.time_shared < _expired_hrs)
    pending_shares.delete()
    logger.info('Deletion complete')


@with_db_session
def get_unique_pending_surveys(is_transfer, session):
    """
    Gets unique pending shares which has passed expiration duration based on batch_id
    :param is_transfer: if the request is to transfer surveys
    :type is_transfer: bool
    :param session A db session
    """
    _expired_hrs = datetime.utcnow() - timedelta(seconds=float(current_app.config["EMAIL_TOKEN_EXPIRY"]))
    pending_shares_ready_for_deletion = session.query(PendingSurveys) \
        .filter(PendingSurveys.time_shared < _expired_hrs) \
        .filter(PendingSurveys.is_transfer == is_transfer) \
        .distinct(PendingSurveys.batch_no)
    unique_batch_record = pending_shares_ready_for_deletion.distinct(PendingSurveys.batch_no)
    return [unique_batch_record.to_pending_surveys_dict() for unique_batch_record in unique_batch_record]


def validate_pending_survey_token(token):
    """
    Validates the share survey token and returns the pending surveys against the batch number
    :param: token
    :param: session
    :return: list of pending surveys
    """
    logger.info('Attempting to verify share/transfer survey', token=token)
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        batch_no = uuid.UUID(decode_email_token(token, duration))
    except SignatureExpired:
        logger.info("Expired share/transfer survey token")
        raise Conflict("Expired share/transfer survey token")
    except (BadSignature, BadData):
        logger.exception("Bad token in validate_pending_survey_token")
        raise NotFound("Unknown batch number in token")
    return get_pending_survey_by_batch_number(batch_no)


@with_db_session
def confirm_pending_survey(batch_no, session):
    """
    confirms share survey by creating a new db session
    :param batch_no: share_survey batch number
    :type batch_no: uuid
    :param session: db session
    :type session: session
    """
    accept_pending_survey(session, batch_no)


def accept_pending_survey(session, batch_no, new_respondent=None):
    """
    Confirms share surveys and transfer surveys
    Creates Enrolment records
    Business Respondent records
    Removes pending shares
    Removes Existing enrolment records and association for transfers
    :param: batch_no
    :param: session
    """
    logger.info('Attempting to confirm pending share survey', batch_no=batch_no)
    pending_surveys = query_pending_survey_by_batch_no(batch_no, session)
    if len(pending_surveys) == 0:
        raise NotFound('Batch number does not exist')
    pending_surveys_list = [pending_survey.to_pending_surveys_dict() for pending_survey in pending_surveys]
    pending_surveys_is_transfer = pending_surveys_list[0].get('is_transfer', False)
    if not new_respondent:
        respondent = get_respondent_by_email(pending_surveys_list[0]['email_address'])
        new_respondent = query_respondent_by_party_uuid(respondent['id'], session)

    for pending_survey in pending_surveys_list:
        business_id = pending_survey['business_id']
        survey_id = pending_survey['survey_id']
        business_respondent = query_business_respondent_by_respondent_id_and_business_id(
            business_id, new_respondent.id, session)
        if not business_respondent:
            # Associate respondent with new business
            business = query_business_by_party_uuid(business_id, session)
            if not business:
                logger.error("Could not find business", business_id=business_id)
                raise InternalServerError("Could not locate business when creating business association")
            business_respondent = BusinessRespondent(business=business, respondent=new_respondent)
        if not is_already_enrolled(survey_id, new_respondent.id, business_id, session):
            try:
                with session.begin_nested():
                    enrolment = Enrolment(business_respondent=business_respondent,
                                          survey_id=pending_survey['survey_id'],
                                          status=EnrolmentStatus.ENABLED)
                    session.add(enrolment)

            except SQLAlchemyError as e:
                logger.exception('Unable to confirm pending survey', batch_no=batch_no)
        else:
            logger.info('Ignoring respondent as already enrolled', business_id=business_id, survey_id=survey_id,
                        email=pending_surveys_list[0]['email_address'])
    delete_pending_survey_by_batch_no(batch_no, session)
    session.commit()
    if pending_surveys_is_transfer:
        try:
            logger.info('About to remove the originator association to the business', business_id=business_id,
                        party_uuid=pending_surveys_list[0]['shared_by'])
            remove_transfer_originator_business_association(pending_surveys_list)
        except SQLAlchemyError as e:
            logger.exception('Unable to remove previous enrolment for originator', batch_no=batch_no,
                             party_uuid=pending_surveys_list[0]['shared_by'])
            raise e
    if pending_surveys_is_transfer:
        send_pending_surveys_confirmation_email(pending_surveys_list, 'transfer_survey_access_confirmation')
    else:
        send_pending_surveys_confirmation_email(pending_surveys_list, 'share_survey_access_confirmation')


@with_db_session
def remove_transfer_originator_business_association(pending_surveys_list, session):
    """
    De-register transfer originator from existing business association.

    :param pending_surveys_list: Pending surveys list
    :type pending_surveys_list: List
    :param session
    :return: On success it returns None, on failure will raise one of many different exceptions
    """
    party_id = pending_surveys_list[0]['shared_by']
    logger.info("Starting to de register transfer originator from business", party_id=party_id)
    transferred_by_respondent = get_respondent_by_id(str(party_id))
    respondent = get_single_respondent_by_email(transferred_by_respondent['emailAddress'], session)
    for pending_survey in pending_surveys_list:
        business_id = pending_survey['business_id']
        survey_id = pending_survey['survey_id']
        logger.info("Starting to de register transfer originator from business", party_id=party_id,
                    business_id=business_id, survey_id=survey_id)
        session.query(Enrolment).filter(
            Enrolment.respondent_id == respondent.id).filter(
            Enrolment.business_id == business_id).filter(
            Enrolment.survey_id == survey_id).delete()
        session.query(BusinessRespondent).filter(
            BusinessRespondent.respondent_id == respondent.id).filter(
            BusinessRespondent.business_id == business_id).delete()
        logger.info("Un enrolled transfer originator for the surveys transferred",
                    party_id=party_id,
                    business_id=business_id, survey_id=survey_id)


def is_already_enrolled(survey_id, respondent_pk, business_id, session):
    """
    returns if enrollment already exists
    :param survey_id
    :param respondent_pk
    :param business_id
    :param session
    :return bool
    """
    enrolment = session.query(Enrolment).filter(and_(Enrolment.survey_id == survey_id,
                                                     Enrolment.business_id == business_id,
                                                     Enrolment.respondent_id == respondent_pk)).first()
    return False if not enrolment else True


@with_db_session
def get_pending_survey_by_batch_number(batch_number, session):
    """
    gets list of share surveys against the batch number
    :param batch_number: share survey batch number
    :type batch_number: uuid
    :param session: db session
    :type session: db session
    :return: list of pending share surveys
    :rtype: list
    """
    pending_surveys = query_pending_survey_by_batch_no(batch_number, session)
    if len(pending_surveys) == 0:
        raise NotFound('Batch number does not exist')
    return [pending_surveys.to_pending_surveys_dict() for pending_surveys in pending_surveys]


# flake8: noqa: C901
@with_quiet_db_session
def post_pending_survey_respondent(party, session):
    """
    Register respondent for share survey/transfer survey.
    This will not create a pending enrolment and will make the respondent active
    :param party: respondent to be created details
    :param session
    :return: created respondent
    """

    # Validation, curation and checks
    expected = ('emailAddress', 'firstName', 'lastName', 'password', 'telephone', 'batch_no')

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

    # Chain of enrolment processes
    translated_party = {
        'party_uuid': party.get('id') or str(uuid.uuid4()),
        'email_address': party['emailAddress'].lower(),
        'first_name': party['firstName'],
        'last_name': party['lastName'],
        'telephone': party['telephone'],
        'status': RespondentStatus.ACTIVE
    }

    # This might look odd but it's done in the interest of keeping the code working in the same way.
    # If raise_for_status in the function raises an error, it would've been caught by @with_db_session,
    # rolled back the db and raised it.  Whether that's something we want is another question.
    try:
        # create new share/transfer survey respondent
        respondent = _add_pending_survey_respondent(session, translated_party, party)
        respondent_dict = respondent.to_respondent_dict()
        # Accept share/transfer surveys surveys
        accept_pending_survey(session, uuid.UUID(party['batch_no']), respondent)
        # Verify created user
        set_user_verified(respondent.email_address)
    except HTTPError:
        logger.error("adding new share survey/transfer survey respondent raised an HTTPError", exc_info=True)
        session.rollback()
        raise
    except SQLAlchemyError:
        logger.exception('adding new share survey/transfer survey respondent raise an SQL Error')
        session.rollback()
        raise

    return respondent_dict


def _add_pending_survey_respondent(session, translated_party, party):
    """
    Create and persist new party entities and attempt to register with auth service.
    Auth fails lead to party entities being rolled back.
    The context manager commits to sub session.
    If final commit fails an account will be in auth not party, this circumstance is unlikely but possible
    :param session: db session
    :type session: db session
    :param translated_party: respondent party dict
    :type translated_party: dict
    :param party: respondent party
    :type party: dict
    """
    try:
        with session.begin_nested():

            # Use a sub transaction to store party data
            # Context manager will manage commits/rollback

            # Create the enrolment respondent-business-survey associations

            respondent = Respondent(**translated_party)
            session.add(respondent)

    except SQLAlchemyError as e:
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

    logger.info("New user has been registered via the auth-service", party_uuid=translated_party['party_uuid'])
    return respondent


def _register_respondent_to_auth(party, session, translated_party):
    # Register user to auth server after successful commit
    oauth_response = OauthClient().create_account(party['emailAddress'].lower(), party['password'])
    if not oauth_response.status_code == 201:
        logger.info('Registering respondent auth service responded with', status=oauth_response.status_code,
                    content=oauth_response.content)

        session.rollback()  # Rollback to SAVEPOINT
        oauth_response.raise_for_status()
    logger.info("New user has been registered via the auth-service", party_uuid=translated_party['party_uuid'])


def send_pending_surveys_confirmation_email(pending_surveys_list, confirmation_email_template):
    """
    Sends confirmation email
    :param pending_surveys_list:
    :type pending_surveys_list:
    :param confirmation_email_template:
    :type confirmation_email_template:
    :return:
    :rtype:
    """
    batch_no = str(pending_surveys_list[0]['batch_no'])
    logger.info('sending confirmation email for pending share', batch_no=batch_no)
    pending_surveys_is_transfer = pending_surveys_list[0].get('is_transfer', False)
    try:
        respondent = get_respondent_by_id(str(pending_surveys_list[0]['shared_by']))
        if pending_surveys_is_transfer:
            confirmation_email_template = 'transfer_survey_access_confirmation'
        else:
            confirmation_email_template = 'share_survey_access_confirmation'
        business_list = []
        for survey in pending_surveys_list:
            business = get_business_by_id(str(survey['business_id']))
            business_list.append(business['name'])
        personalisation = {'NAME': respondent['firstName'],
                           'COLLEAGUE_EMAIL_ADDRESS': pending_surveys_list[0]['email_address'],
                           'BUSINESSES': business_list}
        NotifyGateway(current_app.config).request_to_notify(email=respondent['emailAddress'],
                                                            template_name=confirmation_email_template,
                                                            personalisation=personalisation)
        logger.info('confirmation email for pending share send successfully', batch_no=batch_no)
    # Exception is used to abide by the notify controller. At this point of time the pending share has been accepted
    # hence if the email phase fails it should not disrupt the flow.
    except Exception as e:  # noqa
        logger.error('Error sending confirmation email for pending share', batch_no=batch_no,
                     email=pending_surveys_list[0]['shared_by'])
