import logging
from datetime import datetime, timedelta

import structlog
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ras_party.controllers.queries import query_enrolment_by_business_and_survey_and_status, \
    query_pending_shares_by_business_and_survey
from ras_party.models.models import PendingShares
from ras_party.support.session_decorator import with_query_only_db_session, with_db_session

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
def pending_share_create(business_id, survey_id, email_address, shared_by, session):
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
    :rtype: void
    """
    pending_share = PendingShares(business_id=business_id, survey_id=survey_id, email_address=email_address,
                                  shared_by=shared_by)
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
