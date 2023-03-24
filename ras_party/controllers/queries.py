import logging
import re
from uuid import UUID

import structlog
from sqlalchemy import and_, distinct, func, or_
from sqlalchemy.sql.functions import count

from ras_party.models.models import (
    Business,
    BusinessAttributes,
    BusinessRespondent,
    Enrolment,
    EnrolmentStatus,
    PendingSurveys,
    Respondent,
)
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
    logger.info("Querying enrolment by business_id and survey_id", business_id=business_id, survey_id=survey_id)
    return (
        session.query(Enrolment)
        .filter(Enrolment.business_id == business_id)
        .filter(Enrolment.survey_id == survey_id)
        .filter(or_(Enrolment.status == EnrolmentStatus.ENABLED, Enrolment.status == EnrolmentStatus.PENDING))
    )


def query_pending_surveys_by_business_and_survey(business_id, survey_id, session, is_transfer):
    """
    Query to return total pending share against businesses is and survey id
    :param business_id: business party id
    :param survey_id: survey id
    :param session: db session
    :param is_transfer: boolean if the query is for transfer survey or share survey
    :return: the pending share
    """
    logger.info("Querying pending share by business_id and survey_id", business_id=business_id, survey_id=survey_id)
    return (
        session.query(PendingSurveys)
        .filter(PendingSurveys.business_id == business_id)
        .filter(PendingSurveys.survey_id == survey_id)
        .filter(PendingSurveys.is_transfer == is_transfer)
    )  # noqa


def query_businesses_by_party_uuids(party_uuids, session):
    """
    Query to return businesses based on party uuids

    :param party_uuids: a list of party uuids
    :param session: db session
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

    return session.query(BusinessAttributes).filter(BusinessAttributes.business_id == business_id).all()


def query_business_attributes_by_sample_summary_id(business_id, sample_summary_id, session):
    """
    Query to return all business attributes records based.  Will not error if no matches are found.

    :param business_id: the id of the business
    :param sample_summary_id: the id of the sample
    :param session: A database session
    :return: A list of businessAttributes that match the query parameters
    :rtype: list of BusinessAttributes
    """
    logger.info(
        "Querying business attributes by id and sample summary",
        business_id=business_id,
        sample_summary_id=sample_summary_id,
    )
    conditions = [
        BusinessAttributes.business_id == business_id,
        BusinessAttributes.sample_summary_id == sample_summary_id,
    ]
    return session.query(BusinessAttributes).filter(and_(*conditions)).all()


def query_business_attributes_by_collection_exercise(business_id, collection_exercise_uuids, session):
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


def query_respondent_by_names_and_emails(first_name, last_name, email, page, limit, session):
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

    logger.info("Querying respondents by names and/or email", email=obfuscate_email(email), page=page, limit=limit)

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

    return filtered_records.order_by(Respondent.last_name.asc()).offset(offset).limit(limit), total_count


def query_respondent_by_party_uuid(party_uuid, session):
    """
    Query to return respondent based on party uuid

    :param party_uuid: the party uuid
    :return: respondent or none
    """
    logger.info("Querying respondents by party_uuid", party_uuid=party_uuid)
    return session.query(Respondent).filter(Respondent.party_uuid == UUID(party_uuid)).first()


def query_respondent_by_email(email, session):
    """
    Query to return respondent based on email

    :param email: the party email
    :return: respondent or none
    """
    logger.info("Querying respondents by email")
    return session.query(Respondent).filter(func.lower(Respondent.email_address) == email.lower()).first()


def query_single_respondent_by_email(email, session):
    """
    Query to return respondent based on email.  Must only return 1 result, otherwise it will throw either
    a NoResultFound or MultipleResultsFound exceptions.

    :param email: the party email
    :return: single respondent or exception thrown
    """
    logger.info("Querying respondents by email, expecting exactly one result")
    return session.query(Respondent).filter(func.lower(Respondent.email_address) == email.lower()).one()


def query_respondent_by_pending_email(email, session):
    """
    Query to return respondent based on pending_email_address

    :param email: the party uuid
    :return: respondent or none
    """
    logger.info("Querying respondents by pending email address")
    return session.query(Respondent).filter(func.lower(Respondent.pending_email_address) == email.lower()).first()


def query_business_respondent_by_respondent_id_and_business_id(business_id, respondent_id, session):
    """
    Query to return respondent business associations based on respondent id

    :param business_id:
    :param respondent_id:
    :param session:
    :return: business associations for respondent
    """
    logger.info("Querying business respondent", respondent_id=respondent_id, business_id=business_id)

    response = (
        session.query(BusinessRespondent)
        .filter(and_(BusinessRespondent.business_id == business_id, BusinessRespondent.respondent_id == respondent_id))
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


def get_respondent_password_verification_token(respondent_id, session):
    """
    Query to retrieve the respondent password verification token

    :param respondent_id: the id of the respondent
    :param session:
    :returns: verification token
    """

    logger.info("Retrieving respondent verification token", respondent_id=respondent_id)

    response = session.query(Respondent).filter(Respondent.party_uuid == respondent_id).first()
    return response.password_verification_token


def add_respondent_password_verification_token(respondent_id, token, session):
    """
    Query to update the respondent password verification tokens

    :param respondent_id: id of the respondent
    :param token: the verification token:
    :param session:
    :return: None on success
    """

    logger.info("Adding respondent verification token", respondent_id=respondent_id)

    session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update(
        {Respondent.password_verification_token: token}
    )


def delete_respondent_password_verification_token(respondent_id, session):
    """
    Query to update the respondent password verification tokens

    :param respondent_id: id of the respondent
    :param session:
    :return: None on success
    """

    logger.info("Removing respondent verification token", respondent_id=respondent_id)

    session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update(
        {Respondent.password_verification_token: None}
    )


def query_password_reset_counter(respondent_id, session):
    """
    Query to retrieve the respondent's password reset counter

    :param respondent_id: id of the respondent
    :param session:
    :return: current number of password reset attempts
    """

    logger.info("Querying password reset counter", respondent_id=respondent_id)

    response = session.query(Respondent).filter(Respondent.party_uuid == respondent_id).first()
    return response.password_reset_counter


def increase_password_reset_counter(respondent_id, counter, session):
    """
    Query to increase the respondent's password reset counter

    :param respondent_id: id of the respondent
    :param counter: password reset counter
    :param session:
    :return: None on success
    """

    logger.info("Increasing password reset counter", respondent_id=respondent_id)

    session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update(
        {Respondent.password_reset_counter: counter}
    )


def reset_password_reset_counter(respondent_id, session):
    """
    Query to reset the respondent's password reset counter

    :param respondent_id: id of the respondent
    :param session:
    :return: None on success
    """

    logger.info("Resetting password reset counter", respondent_id=respondent_id)

    session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update(
        {Respondent.password_reset_counter: 0}
    )


def search_business_with_ru_ref(search_query: str, page: int, limit: int, max_rec: int, session):
    """
    This query returns business search on ru reference
    :return: list of businesses
    """
    bound_logger = logger.bind(search_query=search_query)
    bound_logger.info("Query looks like an ru_ref, searching only on ru_ref")
    offset = (page - 1) * limit
    if search_query.isdigit():
        if len(search_query) == 11:
            bound_logger.info("Searching businesses by full ru_ref with search query")
            result = (
                session.query(BusinessAttributes.name, BusinessAttributes.trading_as, Business.business_ref)
                .select_from(BusinessAttributes)
                .join(Business)
                .filter(Business.business_ref == search_query)
                .distinct()
                .all()
            )
            return result, len(result)

        else:
            bound_logger.info("Searching businesses by partial ru_ref with search query")
            pages = (
                session.query(count(distinct(Business.business_ref)))
                .filter(Business.business_ref.ilike(f"%{search_query}%"))
                .distinct()
            )
            result = (
                session.query(BusinessAttributes.name, BusinessAttributes.trading_as, Business.business_ref)
                .select_from(BusinessAttributes)
                .join(Business)
                .filter(Business.business_ref.ilike(f"%{search_query}%"))
                .order_by(Business.business_ref.asc())
                .distinct()
                .limit(limit)
                .offset(offset)
            )
            estimated_total_records = pages.scalar()
            # we don't want to overload database with the search which retrieves more than 10000 records
            # as it's irrelevant to show so many records as a paginated search on frontend
            # hence this 'if' logic will avoid such searches and frontend will ask the user to refine their search
            if pages.scalar() > max_rec:
                return [], estimated_total_records
            return result, estimated_total_records


def search_businesses(search_query: str, page: int, limit: int, max_rec: int, session):
    """
    Query to return list of businesses based on key word search/ business names
    :return: list of businesses
    """
    bound_logger = logger.bind(search_query=search_query)
    bound_logger.info("Searching businesses by name with search query")
    offset = (page - 1) * limit
    # Direct search else normal like search
    regex = re.compile("[@_!#$%^&*()<>?/|}{~:]")
    if len(search_query.split()) == 1 and regex.search(search_query) is None:
        direct_pages = (
            session.query(count(distinct(BusinessAttributes.name)))
            .filter(
                and_(
                    or_(
                        BusinessAttributes.name.ilike(f"{search_query}"),
                        BusinessAttributes.trading_as.ilike(f"{search_query}"),
                    ),
                    BusinessAttributes.collection_exercise.isnot(None),
                )
            )
            .distinct()
        )
        direct_result = (
            session.query(BusinessAttributes.name, BusinessAttributes.trading_as, Business.business_ref)
            .select_from(BusinessAttributes)
            .join(Business)
            .filter(
                and_(
                    or_(
                        BusinessAttributes.name.ilike(f"{search_query}"),
                        BusinessAttributes.trading_as.ilike(f"{search_query}"),
                    ),
                    BusinessAttributes.collection_exercise.isnot(None),
                )
            )
            .order_by(BusinessAttributes.name.asc())
            .distinct()
            .limit(limit)
            .offset(offset)
        )

        estimated_direct_total = direct_pages.scalar()
        # we don't want to overload database with the search which retrieves more than 10000 records
        # as its irrelevant to show so many records as a paginated search on frontend
        # hence this 'if' logic will avoids such searches and frontend will ask the user to refine their search
        if estimated_direct_total > max_rec:
            return [], estimated_direct_total
        if estimated_direct_total != 0:
            return direct_result, estimated_direct_total

    pages = (
        session.query(count(distinct(BusinessAttributes.name)))
        .filter(
            and_(
                or_(
                    BusinessAttributes.name.ilike(f"%{search_query}%"),
                    BusinessAttributes.trading_as.ilike(f"%{search_query}%"),
                ),
                BusinessAttributes.collection_exercise.isnot(None),
            )
        )
        .distinct()
    )
    result = (
        session.query(BusinessAttributes.name, BusinessAttributes.trading_as, Business.business_ref)
        .select_from(BusinessAttributes)
        .join(Business)
        .filter(
            and_(
                or_(
                    BusinessAttributes.name.ilike(f"%{search_query}%"),
                    BusinessAttributes.trading_as.ilike(f"%{search_query}%"),
                ),
                BusinessAttributes.collection_exercise.isnot(None),
            )
        )
        .order_by(BusinessAttributes.name.asc())
        .distinct()
        .limit(limit)
        .offset(offset)
    )
    estimated_total_records = pages.scalar()
    # we don't want to overload database with the search which retrieves more than 10000 records
    # as its irrelevant to show so many records as a paginated search on frontend
    # hence this 'if' logic will avoids such searches and frontend will ask the user to refine their search
    if estimated_total_records > max_rec:
        return [], estimated_total_records
    return result, estimated_total_records


def query_pending_survey_by_batch_no(batch_no, session):
    """
    Query to return pending survey by batch no.
    :param batch_no: UUID
    :return: share surveys
    """
    logger.info("Querying share_surveys", batch_no=batch_no)
    response = session.query(PendingSurveys).filter(PendingSurveys.batch_no == batch_no).all()
    return response


def query_pending_survey_by_shared_by(shared_by, session):
    """
    Query to return pending survey by shared by party id.
    :param shared_by: UUID
    :return: share surveys
    """
    logger.info("Querying share_surveys", shared_by=str(shared_by))
    response = session.query(PendingSurveys).filter(PendingSurveys.shared_by == shared_by).all()
    return response


def delete_pending_survey_by_batch_no(batch_no, session):
    """
    Query to delete existing pending survey by batch no.
    :param batch_no: UUID
    :return: pending surveys
    """
    logger.info("Querying share_surveys", batch_no=batch_no)
    response = session.query(PendingSurveys).filter(PendingSurveys.batch_no == batch_no).delete()
    return response


def query_enrolment_by_survey_business_respondent(respondent_id, business_id, survey_id, session):
    """
    Query to return enrolment based on respondent id, business id and survey

    :param respondent_id:
    :param business_id:
    :param survey_id:
    :return: enrolment for survey and business for respondent
    """

    logger.info("Querying enrolment", respondent_id=respondent_id, business_id=business_id, survey_id=survey_id)

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
        .filter(and_(Enrolment.respondent_id == respondent_id, Enrolment.status != "DISABLED"))
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
