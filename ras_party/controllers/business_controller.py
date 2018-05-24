import uuid

from flask import current_app

from ras_party.controllers.queries import query_business_by_ref, query_business_by_party_uuid, search_businesses
from ras_party.controllers.validate import Validator, Exists
from ras_party.exceptions import RasError
from ras_party.models.models import Business, BusinessAttributes
from ras_party.support.session_decorator import with_db_session


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
        raise RasError("Business with reference does not exist.", reference=ref, status=404)

    if verbose:
        return business.to_business_dict()
    else:
        return business.to_business_summary_dict()


@with_db_session
def get_business_by_id(party_uuid, session, verbose=False, collection_exercise_id=None):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param party_uuid: ID of Party to return
    :type party_uuid: str

    :param verbose: Verbosity of business details

    :param collection_exercise_id: ID of Collection Exercise version of party
    :type collection_exercise_id: str

    :rtype: Business
    """
    try:
        uuid.UUID(party_uuid)
    except ValueError:
        raise RasError(f"'{party_uuid}' is not a valid UUID format for property 'id'", status=400)

    business = query_business_by_party_uuid(party_uuid, session)
    if not business:
        raise RasError("Business with party id does not exist.", party_uuid=party_uuid, status=404)

    if verbose:
        return business.to_business_dict(collection_exercise_id=collection_exercise_id)
    else:
        return business.to_business_summary_dict(collection_exercise_id=collection_exercise_id)


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
        raise RasError([e.split('\n')[0] for e in errors], status=400)

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
def businesses_sample_ce_link(sample, ce_data, session):
    """
    Update business versions to have the correct collection exercise and sample link.

    :param sample: the sample summary id to update.
    :param ce_data: dictionary containing the collectionExerciseId to link with sample.
    :param session: database session.
    """

    v = Validator(Exists('collectionExerciseId'))
    if not v.validate(ce_data):
        raise RasError(v.errors, 400)

    collection_exercise_id = ce_data['collectionExerciseId']

    session.query(BusinessAttributes).filter(BusinessAttributes.sample_summary_id == sample)\
        .update({'collection_exercise': collection_exercise_id})


@with_db_session
def get_businesses_by_search_query(search_query, session):
    businesses = search_businesses(search_query, session)
    businesses = [{"ruref": business[2], "trading_as": business[1], "name": business[0]} for business in businesses]
    return businesses
