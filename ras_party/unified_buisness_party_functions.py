import logging

import structlog
from werkzeug.exceptions import BadRequest

from ras_party.models.models import EnrolmentStatus

logger = structlog.wrap_logger(logging.getLogger(__name__))


def to_unified_dict(model, collection_exercise_id=None, attributes_required=False, associations_required=False):
    attributes = get_attributes_for_collection_exercise(model, collection_exercise_id)
    unified_dict = {
        "id": model.party_uuid,
        "sampleUnitRef": model.business_ref,
        "sampleUnitType": model.UNIT_TYPE,
        "sampleSummaryId": attributes.sample_summary_id,
        "name": attributes.attributes.get("name"),
        "trading_as": attributes.attributes.get("trading_as"),
    }
    if attributes_required:
        unified_dict["attributes"] = attributes.attributes
    if associations_required:
        unified_dict["associations"] = get_respondents_associations(model.respondents)

    return unified_dict


def get_respondents_associations(respondents):
    associations = []
    for business_respondent in respondents:
        respondent_dict = {
            "partyId": business_respondent.respondent.party_uuid,
            "businessRespondentStatus": business_respondent.respondent.status.name,
        }
        enrolments = business_respondent.enrolment
        respondent_dict["enrolments"] = []
        for enrolment in enrolments:
            enrolments_dict = {
                "surveyId": enrolment.survey_id,
                "enrolmentStatus": EnrolmentStatus(enrolment.status).name,
            }
            respondent_dict["enrolments"].append(enrolments_dict)
        associations.append(respondent_dict)
    return associations


def get_attributes_for_collection_exercise(model_attributes, collection_exercise_id=None):
    if collection_exercise_id:
        for attributes in model_attributes.attributes:
            if attributes.collection_exercise == collection_exercise_id:
                return attributes

    try:
        return next((attributes for attributes in model_attributes.attributes if attributes.collection_exercise))
    except StopIteration:
        logger.error("No active attributes for business", reference=model_attributes.business_ref, status=400)
        raise BadRequest("Business with reference does not have any active attributes.")
