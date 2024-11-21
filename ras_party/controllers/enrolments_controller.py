import logging
from uuid import UUID

import structlog
from flask import session
from sqlalchemy.orm.exc import NoResultFound

from ras_party.controllers.queries import (
    query_respondent_by_party_uuid,
    query_respondent_enrolments,
)
from ras_party.models.models import Enrolment
from ras_party.support.session_decorator import with_query_only_db_session

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def respondent_enrolments(
    session: session, party_uuid: UUID, business_id: UUID = None, survey_id: UUID = None, status: int = None
) -> list[Enrolment]:
    """
    returns a list of respondent Enrolments. Business_id, survey_id and status can also be added as conditions
    """

    respondent = query_respondent_by_party_uuid(party_uuid, session)
    if not respondent:
        raise NoResultFound

    return query_respondent_enrolments(session, respondent.id, business_id, survey_id, status)
