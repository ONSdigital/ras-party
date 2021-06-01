import logging

import structlog
from sqlalchemy import and_, distinct, func, or_

from ras_party.models.models import (Business, BusinessAttributes,
                                     BusinessRespondent, Enrolment,
                                     EnrolmentStatus, PendingShares,
                                     Respondent)
from ras_party.support.util import obfuscate_email

logger = structlog.wrap_logger(logging.getLogger(__name__))


def query_enrolment_by_business_and_survey_and_status(business_id, survey_id, session):
    """
    Query to return total enrolments against businesses is and survey id
    :param business_id: business party id
    :param survey_id: survey id
    :param session: db session
    :return: the enrolment
    """
    logger.info(
        "Querying enrolment by business_id and survey_id",
        business_id=business_id,
        survey_id=survey_id,
    )
    return (
        session.query(Enrolment)
        .filter(Enrolment.business_id == business_id)
        .filter(Enrolment.survey_id == survey_id)
        .filter(
            or_(
                Enrolment.status == EnrolmentStatus.ENABLED,
                Enrolment.status == EnrolmentStatus.PENDING,
            )
        )
    )


def query_pending_shares_by_business_and_survey(business_id, survey_id, session):
    """
    Query to return total pending share against businesses is and survey id
    :param business_id: business party id
    :param survey_id: survey id
    :param session: db session
    :return: the pending share
    """
    logger.info(
        "Querying pending share by business_id and survey_id",
        business_id=business_id,
        survey_id=survey_id,
    )
    return (
        session.query(PendingShares)
        .filter(PendingShares.business_id == business_id)
        .filter(PendingShares.survey_id == survey_id)
    )


def query_businesses_by_party_uuids(party_uuids, session):
    """
    Query to return businesses based on party uuids

    :param party_uuids: a list of party uuids
    :return: the businesses
    """
    logger.info("Querying businesses by party_uuids", party_uuids=party_uuids)
    return session.query(Business).filter(Business.party_uuid.in_(party_uuids))


def query_business_by_party_uuid(party_uuid, session):
    """
    Query to return business based on party uuid

    :param party_uuid: the party uuid
    :return: business or none
    :rtype: Business
    """
    logger.info("Querying businesses by party_uuid", party_uuid=party_uuid)

    return session.query(Business).filter(Business.party_uuid == party_uuid).first()


def query_business_by_ref(business_ref, session):
    """
    Query to return business based on business ref
    :param business_ref: the business ref
    :return: business or none
    :rtype: Business
    """
    logger.info("Querying businesses by business_ref", business_ref=business_ref)

    return session.query(Business).filter(Business.business_ref == business_ref).first()


def query_business_attributes(business_id, session):
    """
    Query to return all business attributes records based

    :param business_id: the id of the business
    :param session: A database session
    :return: A list of businessAttributes that match the id
    :rtype: list of BusinessAttributes
    """
    logger.info("Querying business attributes by id", business_id=business_id)

    return (
        session.query(BusinessAttributes)
        .filter(BusinessAttributes.business_id == business_id)
        .all()
    )


def query_business_attributes_by_collection_exercise(
    business_id, collection_exercise_uuids, session
):
    """
    Query to return all business attributes records based.  Will not error if no matches are found.

    :param business_id: the id of the business
    :param collection_exercise_uuids:
    :param session: A database session
    :return: A list of businessAttributes that match the query parameters
    :rtype: list of BusinessAttributes
    """
    logger.info(
        "Querying business attributes by id and collection exercise",
        business_id=business_id,
        collection_exercise_uuids=collection_exercise_uuids,
    )
    conditions = [
        BusinessAttributes.business_id == business_id,
        BusinessAttributes.collection_exercise.in_(collection_exercise_uuids),
    ]
    return session.query(BusinessAttributes).filter(and_(*conditions)).all()


def query_respondent_by_party_uuids(party_uuids, session):
    """
    Query to return respondents based on party uuids

    :param party_uuids: the party uuids
    :return: respondents or empty list
    """
    logger.info("Querying respondents by party_uuids", party_uuids=party_uuids)
    return session.query(Respondent).filter(Respondent.party_uuid.in_(party_uuids))


def query_respondent_by_names_and_emails(
    first_name, last_name, email, page, limit, session
):
    """
    returns respondents which match first_name, last_name and email, ignoring case in all cases
    if any parameter is empty then it is ignored

    :param first_name: only return respondents whose first name starts with this first_name
    :param last_name: only return respondents whose last name starts with this last_name
    :param email: only return respondents whose email address contains starts with this email
    :param page: return this page of a result set
    :param limit: max number of records per page
    :param session:
    """

    logger.info(
        "Querying respondents by names and/or email",
        email=obfuscate_email(email),
        page=page,
        limit=limit,
    )

    conditions = []

    if first_name:
        conditions.append(Respondent.first_name.ilike(f"{first_name}%"))
    if last_name:
        conditions.append(Respondent.last_name.ilike(f"{last_name}%"))
    if email:
        conditions.append(Respondent.email_address.ilike(f"%{email}%"))

    offset = (page - 1) * limit

    filtered_records = session.query(Respondent).filter(and_(*conditions))

    total_count = filtered_records.count()

    return (
        filtered_records.order_by(Respondent.last_name.asc())
        .offset(offset)
        .limit(limit),
        total_count,
    )


def query_respondent_by_party_uuid(party_uuid, session):
    """
    Query to return respondent based on party uuid

    :param party_uuid: the party uuid
    :return: respondent or none
    """
    logger.info("Querying respondents by party_uuid", party_uuid=party_uuid)
    return session.query(Respondent).filter(Respondent.party_uuid == party_uuid).first()


def query_respondent_by_email(email, session):
    """
    Query to return respondent based on email

    :param email: the party email
    :return: respondent or none
    """
    logger.info("Querying respondents by email")
    return (
        session.query(Respondent)
        .filter(func.lower(Respondent.email_address) == email.lower())
        .first()
    )


def query_single_respondent_by_email(email, session):
    """
    Query to return respondent based on email.  Must only return 1 result, otherwise it will throw either
    a NoResultFound or MultipleResultsFound exceptions.

    :param email: the party email
    :return: single respondent or exception thrown
    """
    logger.info("Querying respondents by email, expecting exactly one result")
    return (
        session.query(Respondent)
        .filter(func.lower(Respondent.email_address) == email.lower())
        .one()
    )


def query_respondent_by_pending_email(email, session):
    """
    Query to return respondent based on pending_email_address

    :param email: the party uuid
    :return: respondent or none
    """
    logger.info("Querying respondents by pending email address")
    return (
        session.query(Respondent)
        .filter(func.lower(Respondent.pending_email_address) == email.lower())
        .first()
    )


def query_business_respondent_by_respondent_id_and_business_id(
    business_id, respondent_id, session
):
    """
    Query to return respondent business associations based on respondent id

    :param business_id:
    :param respondent_id:
    :param session:
    :return: business associations for respondent
    """
    logger.info(
        "Querying business respondent",
        respondent_id=respondent_id,
        business_id=business_id,
    )

    response = (
        session.query(BusinessRespondent)
        .filter(
            and_(
                BusinessRespondent.business_id == business_id,
                BusinessRespondent.respondent_id == respondent_id,
            )
        )
        .first()
    )
    return response


def update_respondent_details(respondent_data, respondent_id, session):
    """
    Query to return respondent, respondent_data consists of the following parameters: first_name, last_name,
    telephone.

    :param respondent_data:
    :param respondent_id: id of the respondent
    :param session:
    :return: True on success, False on failure or if any details are missing
    """

    logger.info("Updating respondent details", respondent_id=respondent_id)
    respondent_details = query_respondent_by_party_uuid(respondent_id, session)

    if (
        respondent_details.first_name != respondent_data["firstName"]
        or respondent_details.last_name != respondent_data["lastName"]
        or respondent_details.telephone != respondent_data["telephone"]
    ):
        session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update(
            {
                Respondent.first_name: respondent_data["firstName"],
                Respondent.last_name: respondent_data["lastName"],
                Respondent.telephone: respondent_data["telephone"],
            }
        )

        return True
    return False


def search_businesses(search_query, page, limit, session):
    """
    Query to return list of businesses based on search query

    :param search_query: a string containing space separated list of keywords to search for in name or trading as
    :param page: page to return starting at 1
    :param limit: the maximum number of results to return in a page
    :return: list of businesses
    """
    bound_logger = logger.bind(search_query=search_query)
    bound_logger.info("Searching businesses by name with search query")
    if len(search_query) == 11 and search_query.isdigit():
        bound_logger.info("Query looks like an ru_ref, searching only on ru_ref")
        result = (
            session.query(
                BusinessAttributes.name,
                BusinessAttributes.trading_as,
                Business.business_ref,
            )
            .join(Business)
            .filter(Business.business_ref == search_query)
            .distinct()
            .all()
        )
        if result:
            return result, len(
                result
            )  # ru ref searches do not need to support pagination
        bound_logger.info("Didn't find an ru_ref, searching everything")

    filters = []
    name_filters = []
    trading_as_filters = []

    filters.append(Business.business_ref.like(f"%{search_query}%"))

    key_words = search_query.split()

    for word in key_words:
        name_filters.append(BusinessAttributes.name.ilike(f"%{word}%"))
        trading_as_filters.append(BusinessAttributes.trading_as.ilike(f"%{word}%"))

    filters.append(and_(*name_filters))
    filters.append(and_(*trading_as_filters))

    bound_logger.unbind("search_query")
    query = (
        session.query(
            BusinessAttributes.name,
            BusinessAttributes.trading_as,
            Business.business_ref,
        )
        .join(Business)
        .filter(and_(or_(*filters), BusinessAttributes.collection_exercise.isnot(None)))
        .distinct()
        .order_by(BusinessAttributes.name)
    )  # Build the query

    results = query.limit(limit).offset((page - 1) * limit).all()  # Execute the query
    if page == 1 and len(results) < limit:
        total_business_count = len(results)
    else:
        count_q = query.statement.with_only_columns(
            [func.count(distinct(Business.business_ref))]
        ).order_by(None)
        total_business_count = query.session.execute(count_q).scalar()

    return results, total_business_count


def query_share_survey_by_batch_no(batch_no, session):
    """
    Query to return share survey by batch no.
    :param batch_no: UUID
    :return: share surveys
    """
    logger.info("Querying share_surveys", batch_no=batch_no)
    response = (
        session.query(PendingShares).filter(PendingShares.batch_no == batch_no).all()
    )
    return response


def delete_share_survey_by_batch_no(batch_no, session):
    """
    Query to delete existing share survey by batch no.
    :param batch_no: UUID
    :return: share surveys
    """
    logger.info("Querying share_surveys", batch_no=batch_no)
    response = (
        session.query(PendingShares).filter(PendingShares.batch_no == batch_no).delete()
    )
    return response


def query_enrolment_by_survey_business_respondent(
    respondent_id, business_id, survey_id, session
):
    """
    Query to return enrolment based on respondent id, business id and survey

    :param respondent_id:
    :param business_id:
    :param survey_id:
    :return: enrolment for survey and business for respondent
    """

    logger.info(
        "Querying enrolment",
        respondent_id=respondent_id,
        business_id=business_id,
        survey_id=survey_id,
    )

    response = (
        session.query(Enrolment)
        .filter(
            and_(
                Enrolment.respondent_id == respondent_id,
                Enrolment.business_id == business_id,
                Enrolment.survey_id == survey_id,
            )
        )
        .first()
    )
    return response


def query_all_non_disabled_enrolments_respondent(respondent_id, session):
    """
    Query to return all non disabled enrolments based on respondent id

    :param respondent_id:  the id column from the respondent (integer not uuid)
    :return: enrolments for the respondent
    """

    logger.info("Querying all enrolments for respondent", respondent_id=respondent_id)

    response = (
        session.query(Enrolment)
        .filter(
            and_(
                Enrolment.respondent_id == respondent_id, Enrolment.status != "DISABLED"
            )
        )
        .all()
    )
    return response


def count_enrolment_by_survey_business(business_id, survey_id, session):
    """
    Query to return count of enrolments for given business id and survey

    :param business_id:
    :param survey_id:
    :return: Integer count of number of enrolments
    """
    logger.info("Querying enrolment", business_id=business_id, survey_id=survey_id)
    response = (
        session.query(Enrolment)
        .filter(
            and_(
                Enrolment.business_id == business_id,
                Enrolment.survey_id == survey_id,
                Enrolment.status == EnrolmentStatus.ENABLED,
            )
        )
        .count()
    )
    return response
