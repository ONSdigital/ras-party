import logging
import uuid

import structlog
from flask import current_app
from werkzeug.exceptions import BadRequest, NotFound

import unified_buisness_party_functions
from ras_party.controllers.queries import (
    query_business_attributes,
    query_business_attributes_by_collection_exercise,
    query_business_by_party_uuid,
    query_business_by_ref,
    query_businesses_by_party_uuids,
    search_business_with_ru_ref,
    search_businesses,
)
from ras_party.controllers.validate import Exists, Validator
from ras_party.models.models import Business, BusinessAttributes
from ras_party.support.session_decorator import (
    with_db_session,
    with_query_only_db_session,
)

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def get_business_by_ref(retrieve_associations, ref, session):
    """
    Get a Business by its unique business reference

    :param ref: Reference of the Business to return
    :type ref: str
    :returns: A business object containing the data for the business
    :rtype: Business
    """
    business = query_business_by_ref(ref, session)
    if not business:
        logger.info("Business with reference does not exist.", ru_ref=ref)
        raise NotFound("Business with reference does not exist.")

    return unified_buisness_party_functions.to_unified_dict(business, collection_exercise_id=None, attributes_required=True, associations_required=retrieve_associations)


@with_query_only_db_session
def get_businesses_by_ids(party_uuids, session):
    """
    Get a list of businesses by party id.

    :param party_uuids: A list of party_ids' to search on
    :param session: A database session
    :returns: A list of businesses
    :raises BadRequest: Raised if any of the uuids provided aren't valid uuids
    """
    for party_uuid in party_uuids:
        try:
            uuid.UUID(party_uuid)
        except ValueError:
            logger.info("Invalid party uuid value", party_uuid=party_uuid)
            raise BadRequest(f"'{party_uuid}' is not a valid UUID format for property 'id'")

    businesses = query_businesses_by_party_uuids(party_uuids, session)
    return [unified_buisness_party_functions.to_unified_dict(business) for business in businesses]


@with_query_only_db_session
def get_business_attributes(business_id, session, collection_exercise_ids=None):
    """
    Get a list of businesses by business id and (optionally) collection exercise ids

    The result is keyed on collection_exercise, so if the collection_exercise is missing, it won't be included
    in the records.

    :param business_id: A business's uuid
    :param collection_exercise_ids: A list of collection exercise ids
    :param session: A database session
    :returns: A dict of BusinessAttributes, keyed by the collection_exercise id
    :rtype: dict of (str, BusinessAttributes)
    :raises BadRequest: Raised if any of the uuids provided aren't valid uuids
    """
    try:
        uuid.UUID(business_id)
    except ValueError:
        logger.warning("Invalid party uuid value", business_id=business_id)
        raise BadRequest(f"'{business_id}' is not a valid UUID format for property 'id'")

    if collection_exercise_ids:
        for collection_exercise_id in collection_exercise_ids:
            try:
                uuid.UUID(collection_exercise_id)
            except ValueError:
                logger.warning("Invalid collection exercise uuid value", collection_exercise_id=collection_exercise_id)
                raise BadRequest(f"'{collection_exercise_id}' is not a valid UUID format for property 'id'")
        attributes = query_business_attributes_by_collection_exercise(business_id, collection_exercise_ids, session)
    else:
        attributes = query_business_attributes(business_id, session)

    return {
        attribute.collection_exercise: attribute.to_dict() for attribute in attributes if attribute.collection_exercise
    }


@with_query_only_db_session
def get_business_by_id(party_uuid, session, verbose=False, collection_exercise_id=None):
    """
    Get a Business by its Party ID

    :param party_uuid: ID of Party to return
    :type party_uuid: str
    :param verbose: Verbosity of business details
    :param collection_exercise_id: ID of Collection Exercise version of party
    :type collection_exercise_id: str
    :returns: A business object containing the data for the business
    :rtype: Business
    :raises BadRequest: Raised if the party_uuid is an invalid uuid
    :raises NotFound: Raised if there isn't a business that has that party_uuid
    """
    try:
        uuid.UUID(party_uuid)
    except ValueError:
        logger.info("Invalid party uuid value", party_uuid=party_uuid)
        raise BadRequest(f"'{party_uuid}' is not a valid UUID format for property 'id'")

    business = query_business_by_party_uuid(party_uuid, session)
    if not business:
        logger.info("Business with id does not exist", party_uuid=party_uuid)
        raise NotFound("Business with party id does not exist")

    if verbose:
        return business.to_business_dict(collection_exercise_id=collection_exercise_id)

    return unified_buisness_party_functions.to_unified_dict(business, collection_exercise_id=collection_exercise_id)


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
    errors = Business.validate(party_data, current_app.config["PARTY_SCHEMA"])
    if errors:
        errors = [e.split("\n")[0] for e in errors]
        logger.debug(errors)
        raise BadRequest(errors)

    business = query_business_by_ref(party_data["sampleUnitRef"], session)
    if business:
        party_data["id"] = str(business.party_uuid)
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

    v = Validator(Exists("collectionExerciseId"))
    if not v.validate(ce_data):
        logger.debug(v.errors)
        raise BadRequest(v.errors)

    collection_exercise_id = ce_data["collectionExerciseId"]

    session.query(BusinessAttributes).filter(BusinessAttributes.sample_summary_id == sample).update(
        {"collection_exercise": collection_exercise_id}
    )


@with_query_only_db_session
def get_businesses_by_search_query(
    search_query: str, page: int, limit: int, is_ru_ref_search: bool, max_rec: int, session
):
    """
    Controller to get the search result based on mandatory arguments
    """
    if limit is None or search_query is None or page is None or is_ru_ref_search is None or max_rec is None:
        raise BadRequest("limit, search_query, page, max_rec and is_ru_ref_search  are required")
    if is_ru_ref_search:
        businesses, total_business_count = search_business_with_ru_ref(search_query, page, limit, max_rec, session)
    else:
        businesses, total_business_count = search_businesses(search_query, page, limit, max_rec, session)
    businesses = [{"ruref": business[2], "trading_as": business[1], "name": business[0]} for business in businesses]
    return businesses, total_business_count


@with_db_session
def delete_attributes_by_sample_summary_id(sample_summary_id: str, session) -> None:
    """
    Delete all the business attributes for a given sample_summary_id.

    :param sample_summary_id: A sample summary id
    :param session: A db session
    """
    logger.info("Searching for business attributes to delete by sample summary id", sample_summary_id=sample_summary_id)
    try:
        uuid.UUID(sample_summary_id)
    except ValueError:
        logger.info("Invalid sample_summary_id value", sample_summary_id=sample_summary_id)
        raise BadRequest(f"'{sample_summary_id}' is not a valid UUID format")
    attributes = session.query(BusinessAttributes).filter(BusinessAttributes.sample_summary_id == sample_summary_id)
    attribute_count = attributes.count()
    if attribute_count > 0:
        attributes.delete()
        logger.info(
            "Successfully deleted attributes", sample_summary_id=sample_summary_id, records_deleted=attribute_count
        )
    else:
        logger.info("No attributes to delete", sample_summary_id=sample_summary_id)
