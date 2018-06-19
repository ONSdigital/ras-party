from flask import current_app

from ras_party.controllers.queries import query_business_by_party_uuid, query_business_by_ref
from ras_party.controllers.queries import query_respondent_by_party_uuid
from ras_party.exceptions import RasError
from ras_party.models.models import Business, Respondent
from ras_party.support.session_decorator import with_db_session


@with_db_session
def parties_post(party_data, session):
    """
    Post a new party (with sampleUnitType B)

    :param party_data: packet containing the data to post
    :type party_data: JSON data maching the schema described in schemas/party_schema.json
    """
    errors = Business.validate(party_data, current_app.config['PARTY_SCHEMA'])
    if errors:
        raise RasError([e.split('\n')[0] for e in errors], status=400)

    if party_data['sampleUnitType'] != Business.UNIT_TYPE:
        raise RasError('sampleUnitType must be of type', type=Business.UNIT_TYPE, status=400)

    business = query_business_by_ref(party_data['sampleUnitRef'], session)
    if business:
        party_data['id'] = str(business.party_uuid)
        business.add_versioned_attributes(party_data)
        session.merge(business)
    else:
        business = Business.from_party_dict(party_data)
        session.add(business)
    return business.to_post_response_dict()


@with_db_session
def get_party_by_ref(sample_unit_type, sample_unit_ref, session):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param sample_unit_ref: Reference of the Party to return
    :type sample_unit_ref: str

    :rtype: Party
    """
    if sample_unit_type != Business.UNIT_TYPE:
        raise RasError(f"{sample_unit_type} is not a valid value for sampleUnitType. Must be one of ['B']", status=400)
    business = query_business_by_ref(sample_unit_ref, session)
    if not business:
        raise RasError("Business with reference does not exist.", refernce=sample_unit_ref, status=404)

    return business.to_party_dict()


@with_db_session
def get_party_by_id(sample_unit_type, id, session):
    if sample_unit_type == Business.UNIT_TYPE:
        business = query_business_by_party_uuid(id, session)
        if not business:
            raise RasError("Business with id does not exist.", business_id=id, status=404)
        return business.to_party_dict()
    elif sample_unit_type == Respondent.UNIT_TYPE:
        respondent = query_respondent_by_party_uuid(id, session)
        if not respondent:
            raise RasError("Respondent with id does not exist.", respondent_id=id, status=404)
        return respondent.to_party_dict()
    else:
        raise RasError(f"{sample_unit_type} is not a valid value for sampleUnitType. Must be one of ['B', 'BI']",
                       status=400)


def get_business_with_respondents_filtered_by_survey(sample_unit_type, id, survey_id):
    business = get_party_by_id(sample_unit_type, id)

    filtered_associations = []
    for association in business['associations']:

        filtered_association = {'partyId': association['partyId']}

        filtered_enrolments = filter_enrolments(association['enrolments'], survey_id)

        if filtered_enrolments:
            filtered_association['enrolments'] = filtered_enrolments
            filtered_associations.append(filtered_association)

    business['associations'] = filtered_associations

    return business


def filter_enrolments(existing_enrolments, survey_id):
    filtered_enrolments = []
    for enrolment in existing_enrolments:
        if enrolment['surveyId'] == survey_id:
            filtered_enrolments.append(enrolment)
    return filtered_enrolments
