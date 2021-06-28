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
from ras_party.controllers.account_controller import set_user_verified
from ras_party.controllers.queries import query_enrolment_by_business_and_survey_and_status, \
    query_pending_shares_by_business_and_survey, query_share_survey_by_batch_no, query_business_by_party_uuid, \
    query_respondent_by_party_uuid, query_business_respondent_by_respondent_id_and_business_id, \
    delete_share_survey_by_batch_no
from ras_party.controllers.respondent_controller import get_respondent_by_email
from ras_party.controllers.validate import Validator, Exists
from ras_party.models.models import PendingShares, BusinessRespondent, Enrolment, EnrolmentStatus, RespondentStatus, \
    Respondent
from ras_party.support.session_decorator import with_query_only_db_session, with_db_session, with_quiet_db_session
from ras_party.support.verification import decode_email_token

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def get_users_enrolled_and_pending_share_against_business_and_survey(business_id, survey_id, session):
    """
    Get total users count who are already enrolled and pending share survey against business id and survey id
    Returns total user count
    :param business_id: business party id
    :type business_id: str
    :param survey_id: survey id
    :type survey_id: str
    :param session: db session
    :rtype: int
    """
    bound_logger = logger.bind(business_id=business_id, survey_id=survey_id)
    bound_logger.info('Attempting to get enrolled users')
    enrolled_users = query_enrolment_by_business_and_survey_and_status(business_id, survey_id, session)
    bound_logger.info('Attempting to get pending survey users')
    pending_survey_users = query_pending_shares_by_business_and_survey(business_id, survey_id, session)
    total_users = enrolled_users.count() + pending_survey_users.count()
    bound_logger.info(f'total users count {total_users}')
    return total_users


@with_db_session
def pending_share_create(business_id, survey_id, email_address, shared_by, batch_number, session):
    """
    creates a new record for pending share
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
    :rtype: void
    """
    pending_share = PendingShares(business_id=business_id, survey_id=survey_id, email_address=email_address,
                                  shared_by=shared_by, batch_no=batch_number)
    session.add(pending_share)


@with_db_session
def delete_pending_shares(session):
    """
    Deletes all the existing pending shares which has passed expiration duration
    :param session A db session
    """
    _expired_hrs = datetime.utcnow() - timedelta(seconds=float(current_app.config["EMAIL_TOKEN_EXPIRY"]))
    pending_shares = session.query(PendingShares).filter(PendingShares.time_shared < _expired_hrs)
    pending_shares.delete()
    logger.info('Deletion complete')


@with_db_session
def get_unique_pending_shares(session):
    """
    Gets unique pending shares which has passed expiration duration based on batch_id
    :param session A db session
    """
    _expired_hrs = datetime.utcnow() - timedelta(seconds=float(current_app.config["EMAIL_TOKEN_EXPIRY"]))
    pending_shares_ready_for_deletion = session.query(PendingShares).filter(PendingShares.time_shared < _expired_hrs) \
        .distinct(PendingShares.batch_no)
    unique_batch_record = pending_shares_ready_for_deletion.distinct(PendingShares.batch_no)
    return [unique_batch_record.to_share_dict() for unique_batch_record in unique_batch_record]


def validate_share_survey_token(token):
    """
    Validates the share survey token and returns the pending shares against the batch number
    :param: token
    :param: session
    :return: list of pending shares
    """
    logger.info('Attempting to verify share survey', token=token)
    try:
        duration = current_app.config["EMAIL_TOKEN_EXPIRY"]
        batch_no = uuid.UUID(decode_email_token(token, duration))
    except SignatureExpired:
        logger.info("Expired share survey token")
        raise Conflict("Expired share survey token")
    except (BadSignature, BadData):
        logger.exception("Bad token in validate_share_survey_token")
        raise NotFound("Unknown batch number in token")
    return get_share_survey_by_batch_number(batch_no)


@with_db_session
def confirm_share_survey(batch_no, session):
    """
    confirms share survey by creating a new db session
    :param batch_no: share_survey batch number
    :type batch_no: uuid
    :param session: db session
    :type session: session
    """
    accept_share_survey(session, batch_no)


def accept_share_survey(session, batch_no, new_respondent=None):
    """
    Confirms share surveys
    Creates Enrolment records
    Business Respondent records
    Removes pending shares
    :param: batch_no
    :param: session
    """
    logger.info('Attempting to confirm pending share survey', batch_no=batch_no)
    share_surveys = query_share_survey_by_batch_no(batch_no, session)
    if len(share_surveys) == 0:
        raise NotFound('Batch number does not exist')
    share_surveys_list = [share_survey.to_share_dict() for share_survey in share_surveys]
    if not new_respondent:
        respondent = get_respondent_by_email(share_surveys_list[0]['email_address'])
        new_respondent = query_respondent_by_party_uuid(respondent['id'], session)

    for pending_share_survey in share_surveys_list:
        business_id = pending_share_survey['business_id']
        survey_id = pending_share_survey['survey_id']
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
                                          survey_id=pending_share_survey['survey_id'],
                                          status=EnrolmentStatus.ENABLED)
                    session.add(enrolment)

            except SQLAlchemyError as e:
                logger.exception('Unable to confirm pending share survey', batch_no=batch_no)
        else:
            logger.info('Ignoring respondent as already enrolled', business_id=business_id, survey_id=survey_id,
                        email=share_surveys_list[0]['email_address'])
        delete_share_survey_by_batch_no(batch_no, session)


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
def get_share_survey_by_batch_number(batch_number, session):
    """
    gets list of share surveys against the batch number
    :param batch_number: share survey batch number
    :type batch_number: uuid
    :param session: db session
    :type session: db session
    :return: list of pending share surveys
    :rtype: list
    """
    share_surveys = query_share_survey_by_batch_no(batch_number, session)
    if len(share_surveys) == 0:
        raise NotFound('Batch number does not exist')
    return [share_survey.to_share_dict() for share_survey in share_surveys]


# flake8: noqa: C901
@with_quiet_db_session
def post_share_survey_respondent(party, session):
    """
    Register respondent for share survey. This will not create a pending enrolment and will make the respondent active
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
        # create new share survey respondent
        respondent = _add_share_survey_respondent(session, translated_party, party)
        # Accept share surveys
        accept_share_survey(session, uuid.UUID(party['batch_no']), respondent)
        # Verify created user
        set_user_verified(respondent.email_address)
    except HTTPError:
        logger.error("adding new share survey respondent raised an HTTPError", exc_info=True)
        session.rollback()
        raise

    return respondent.to_respondent_dict()


def _add_share_survey_respondent(session, translated_party, party):
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

        session.commit()  # Full session commit

    logger.info("New user has been registered via the auth-service", party_uuid=translated_party['party_uuid'])
    return respondent
