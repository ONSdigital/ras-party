import logging

from flask import current_app
import structlog

from ras_party.controllers.queries import query_business_by_party_uuid, query_business_by_ref
from ras_party.controllers.queries import query_respondent_by_party_uuid
from ras_party.controllers.validate import Validator, IsIn
from ras_party.exceptions import RasError
from ras_party.models.models import Business, Respondent
from ras_party.support.session_decorator import with_db_session

log = structlog.wrap_logger(logging.getLogger(__name__))


@with_db_session
def parties_post(party_data, session):
    """
    Post a new party (with sampleUnitType B)

    :param party_data: packet containing the data to post
    :type party_data: JSON data maching the schema described in schemas/party_schema.json
    """
    errors = Business.validate(party_data, current_app.config['PARTY_SCHEMA'])
    if errors:
        raise RasError([e.split('\n')[0] for e in errors], status_code=400)

    if party_data['sampleUnitType'] != Business.UNIT_TYPE:
        raise RasError([{'message': 'sampleUnitType must be of type ({})'.format(Business.UNIT_TYPE)}], status_code=400)

    existing_business = query_business_by_ref(party_data['sampleUnitRef'], session)
    if existing_business:
        party_data['id'] = str(existing_business.party_uuid)

    b = Business.from_party_dict(party_data)
    session.merge(b)
    return b.to_party_dict()


@with_db_session
def get_party_by_ref(sample_unit_type, sample_unit_ref, session):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param sample_unit_ref: Reference of the Party to return
    :type sample_unit_ref: str

    :rtype: Party
    """
    v = Validator(IsIn('sampleUnitType', 'B'))
    if not v.validate({'sampleUnitType': sample_unit_type}):
        raise RasError(v.errors, status_code=400)

    business = query_business_by_ref(sample_unit_ref, session)
    if not business:
        raise RasError("Business with reference '{}' does not exist.".format(sample_unit_ref), status_code=404)

    return business.to_party_dict()


@with_db_session
def get_party_by_id(sample_unit_type, id, session):
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sample_unit_type}):
        raise RasError(v.errors, status_code=400)

    if sample_unit_type == Business.UNIT_TYPE:
        business = query_business_by_party_uuid(id, session)
        if not business:
            raise RasError("Business with id '{}' does not exist.".format(id), status_code=404)

        return business.to_party_dict()

    elif sample_unit_type == Respondent.UNIT_TYPE:
        respondent = query_respondent_by_party_uuid(id, session)
        if not respondent:
            return RasError("Respondent with id '{}' does not exist.".format(id), status_code=404)

        return respondent.to_party_dict()
