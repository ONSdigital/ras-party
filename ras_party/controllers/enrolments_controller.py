import logging
from uuid import UUID

import structlog
from flask import session
from sqlalchemy.orm.exc import NoResultFound

from ras_party.controllers.queries import (
    query_enrolments_by_parameters,
    query_respondent_by_party_uuid,
)
from ras_party.models.models import Enrolment
from ras_party.support.session_decorator import with_query_only_db_session

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def enrolments_by_parameters(
    session: session, party_uuid: UUID = None, business_id: UUID = None, survey_id: UUID = None, status: int = None
) -> list[Enrolment]:
    """
    returns a list of Enrolments based on provided parameters
    """

    if party_uuid:
        respondent = query_respondent_by_party_uuid(party_uuid, session)
        if not respondent:
            raise NoResultFound

    respondent_id = respondent.id if party_uuid else None

    return query_enrolments_by_parameters(session, respondent_id, business_id, survey_id, status)
