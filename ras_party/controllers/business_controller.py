
from flask import current_app
from ras_common_utils.ras_error.ras_error import RasError
from structlog import get_logger

from ras_party.controllers.error_decorator import translate_exceptions
from ras_party.controllers.queries import query_business_by_ref, query_business_by_party_uuid
from ras_party.controllers.validate import Validator, IsUuid
from ras_party.models.models import Business
from ras_party.support.session_decorator import with_db_session


log = get_logger()


@translate_exceptions
@with_db_session
def get_business_by_ref(ref, session, verbose=False):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :param verbose: Verbosity of business details

    :rtype: Business
    """
    business = query_business_by_ref(ref, session)
    if not business:
        raise RasError("Business with reference '{}' does not exist.".format(ref), status_code=404)

    if verbose:
        return business.to_business_dict()
    else:
        return business.to_business_summary_dict()


@translate_exceptions
@with_db_session
def get_business_by_id(party_uuid, session, verbose=False):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param party_uuid: ID of Party to return
    :type party_uuid: str

    :param verbose: Verbosity of business details

    :rtype: Business
    """
    v = Validator(IsUuid('id'))
    if not v.validate({'id': party_uuid}):
        raise RasError(v.errors, status_code=400)

    business = query_business_by_party_uuid(party_uuid, session)
    if not business:
        raise RasError("Business with party id '{}' does not exist.".format(party_uuid), status_code=404)

    if verbose:
        return business.to_business_dict()
    else:
        return business.to_business_summary_dict()


@translate_exceptions
@with_db_session
def businesses_post(business_data, session):
    """
    Create a new business in the database based on the supplied data dictionary.

    :param business_data: dictionary containing the attributes of the business.
    :param session: database session.
    :return: Jsonified representation of the created business.
    """
    party_data = Business.to_party(business_data)

    # FIXME: this is incorrect, it doesn't make sense to require sampleUnitType for the concrete endpoints
    errors = Business.validate(party_data, current_app.config['PARTY_SCHEMA'])
    if errors:
        raise RasError([e.split('\n')[0] for e in errors], status_code=400)

    existing_business = query_business_by_ref(party_data['sampleUnitRef'], session)
    if existing_business:
        party_data['id'] = str(existing_business.party_uuid)

    b = Business.from_party_dict(party_data)
    session.merge(b)
    return b.to_business_dict()
