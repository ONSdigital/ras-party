import logging

import structlog
from flask import current_app
from werkzeug.exceptions import BadRequest, Conflict

from ras_party.controllers.queries import (
    query_business_attributes_by_sample_summary_id,
    query_business_by_ref,
)
from ras_party.models.models import Business
from ras_party.support.session_decorator import with_db_session

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_db_session
def parties_post(party_data, session):
    """
    Post a new party (with sampleUnitType B)

    :param party_data: packet containing the data to post
    :type party_data: JSON data maching the schema described in schemas/party_schema.json
    """
    logger.info("post party data in controller", party_data=party_data)
    validate_business(party_data)

    business = query_business_by_ref(party_data["sampleUnitRef"], session)
    if business:
        party_data["id"] = str(business.party_uuid)
        ba = query_business_attributes_by_sample_summary_id(business.party_uuid, party_data["sampleSummaryId"], session)
        if ba:
            raise Conflict("party already exists for sample")
        else:
            business.add_versioned_attributes(party_data)
        session.merge(business)
    else:
        business = Business.from_party_dict(party_data)
        session.add(business)
    return business.to_post_response_dict()


def validate_business(party_data: dict):
    errors = Business.validate(party_data, current_app.config["PARTY_SCHEMA"])
    if errors:
        logger.info("party schema validation failed", errors=[e.split("\n")[0] for e in errors])
        raise BadRequest([e.split("\n")[0] for e in errors])
    if party_data["sampleUnitType"] != Business.UNIT_TYPE:
        logger.info("Wrong sampleUnitType", type=party_data["sampleUnitType"])
        raise BadRequest(f"sampleUnitType must be of type {Business.UNIT_TYPE}")


@with_db_session
def parties_patch(party_data, session):
    """
    Post a new party (with sampleUnitType B)

    :param party_data: packet containing the data to post
    :type party_data: JSON data maching the schema described in schemas/party_schema.json
    """
    logger.info("patch party data in controller", party_data=party_data)
    validate_business(party_data)

    business = query_business_by_ref(party_data["sampleUnitRef"], session)
    if business:
        party_data["id"] = str(business.party_uuid)
        business.add_versioned_attributes(party_data)
        session.merge(business)
    else:
        business = Business.from_party_dict(party_data)
        session.add(business)
    return business.to_post_response_dict()


def filter_enrolments(existing_enrolments, survey_id, enrolment_status=None):
    filtered_enrolments = []
    for enrolment in existing_enrolments:
        if enrolment["surveyId"] == survey_id:
            filtered_enrolments.append(enrolment)

    if enrolment_status:
        for enrolment in filtered_enrolments:
            if enrolment["enrolmentStatus"] not in enrolment_status:
                filtered_enrolments.remove(enrolment)
    return filtered_enrolments
