import logging
from collections import defaultdict
from uuid import UUID

import structlog
from flask import session
from sqlalchemy.orm.exc import NoResultFound

from ras_party.controllers.queries import (
    query_enrolment_by_survey_business_respondent,
    query_respondent_by_party_uuid,
    query_respondent_enrolments,
)
from ras_party.controllers.survey_controller import get_surveys_details
from ras_party.models.models import Enrolment, RespondentStatus
from ras_party.support.session_decorator import with_query_only_db_session

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def respondent_enrolments(
    session: session, party_uuid: UUID, business_id: UUID = None, survey_id: UUID = None, status: int = None
) -> list[Enrolment]:
    """
    returns a list of respondent enrolments with business and survey details
    """

    respondent = query_respondent_by_party_uuid(party_uuid, session)
    if not respondent:
        raise NoResultFound

    enrolments = query_respondent_enrolments(session, respondent.id, business_id, survey_id, status)

    if enrolments.rowcount == 0:
        return []

    surveys_details = get_surveys_details()
    enrolments_map = defaultdict(_business_survey_details)

    for enrolment in enrolments:
        business_ref = enrolment.business_ref
        survey_id = enrolment.survey_id

        enrolments_map[business_ref]["business_name"] = enrolment.attributes["name"]
        enrolments_map[business_ref]["business_id"] = enrolment.business_id
        enrolments_map[business_ref]["ru_ref"] = enrolment.business_ref
        enrolments_map[business_ref]["trading_as"] = enrolment.attributes["trading_as"]
        enrolments_map[business_ref]["survey_details"].append(
            {
                "id": survey_id,
                "long_name": surveys_details.get(survey_id)["long_name"],
                "short_name": surveys_details.get(survey_id)["short_name"],
                "ref": surveys_details.get(survey_id)["ref"],
                "enrolment_status": enrolment.status,
            }
        )

    return list(enrolments_map.values())


def _business_survey_details() -> dict:
    return {"survey_details": []}


@with_query_only_db_session
def is_respondent_enrolled(party_uuid: UUID, business_id: UUID, survey_id: UUID, session: session) -> bool:
    respondent = query_respondent_by_party_uuid(party_uuid, session)

    if respondent and respondent.status == RespondentStatus.ACTIVE:
        enrolment = query_enrolment_by_survey_business_respondent(respondent.id, business_id, survey_id, session)
        if enrolment:
            return True
    return False
