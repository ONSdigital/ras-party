import logging
import uuid

import structlog
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers.account_controller import (
    change_respondent,
    get_single_respondent_by_email,
)
from ras_party.controllers.queries import (
    query_respondent_by_email,
    query_respondent_by_names_and_emails,
    query_respondent_by_party_uuid,
    query_respondent_by_party_uuids,
    update_respondent_details,
)
from ras_party.models.models import (
    BusinessRespondent,
    Enrolment,
    PendingEnrolment,
    Respondent,
)
from ras_party.support.session_decorator import (
    with_db_session,
    with_query_only_db_session,
)
from ras_party.support.util import obfuscate_email

logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_query_only_db_session
def get_respondent_by_ids(ids, session):
    """
    Get respondents by Party IDs, if an id doesn't exist then nothing is return for that id.
    Returns multiple parties

    :param ids: the ids of Respondent to return
    :type ids: str
    :rtype: Respondent
    """
    respondents = query_respondent_by_party_uuids(ids, session)
    return [respondent.to_respondent_dict() for respondent in respondents]


@with_query_only_db_session
def get_respondents_by_name_and_email(first_name, last_name, email, page, limit, session):
    """
    Get respondents that match the provided parameters

    :param first_name: only return respondents whose first name starts with this first_name
    :param last_name: only return respondents whose last name starts with this last_name
    :param email: only return respondents whose email address contains starts with this email
    :param page: page of result set to return starting at 1
    :param limit: maximum amount per page
    :param session:
    :return: Respondents
    """
    respondents, record_count = query_respondent_by_names_and_emails(first_name, last_name, email, page, limit, session)
    return {"data": [respondent.to_respondent_dict() for respondent in respondents], "total": record_count}


@with_query_only_db_session
def get_respondent_by_id(respondent_id, session):
    """
    Get a Respondent by its Party ID. Returns a single Party

    :param respondent_id: ID of Respondent to return
    :type respondent_id: str
    :return: An object representing a respondent, if it exists.
    :rtype: Respondent
    """
    try:
        uuid.UUID(respondent_id)
    except ValueError:
        logger.info("respondent_id value is not a valid UUID", respondent_id=respondent_id)
        raise BadRequest(f"'{respondent_id}' is not a valid UUID format for property 'id'")

    respondent = query_respondent_by_party_uuid(respondent_id, session)
    if not respondent:
        logger.info("Respondent with party id does not exist", respondent_id=respondent_id)
        raise NotFound("Respondent with party id does not exist")

    return respondent.to_respondent_dict()


@with_db_session
def update_respondent_mark_for_deletion(email, session):
    """
    Update respondent flag mark_for_deletion

    :param email: email of Respondent to be marked for deletion
    :type email: str
    :param session:
    :return: On Success it returns None, on failure will raise exceptions
    """
    respondent = query_respondent_by_email(email, session)
    if respondent:
        try:
            session.query(Respondent).filter(Respondent.party_uuid == respondent.party_uuid).update(
                {Respondent.mark_for_deletion: True}
            )
            return "respondent successfully marked for deletion", 202
        except (SQLAlchemyError, Exception) as error:
            logger.error("error with update respondent mark for deletion", error)
            return "something went wrong", 500
    else:
        return "respondent does not exist", 404


@with_db_session
def delete_respondents_marked_for_deletion(session):
    """
    Deletes all the existing respondents and there associated data which are marked for deletion

    :param session A db session
    """
    respondents = session.query(Respondent).filter(Respondent.mark_for_deletion == True)  # noqa
    for respondent in respondents:
        session.query(Enrolment).filter(Enrolment.respondent_id == respondent.id).delete()
        session.query(BusinessRespondent).filter(BusinessRespondent.respondent_id == respondent.id).delete()
        session.query(PendingEnrolment).filter(PendingEnrolment.respondent_id == respondent.id).delete()
        session.query(Respondent).filter(Respondent.id == respondent.id).delete()


@with_db_session
def delete_respondent_by_email(email, session):
    """
    Delete a Respondent by its email

    :param email: Id of Respondent to delete
    :type email: str
    :return: On success it returns None, on failure will raise one of many different exceptions
    """
    logger.info("Starting to delete respondent", email=obfuscate_email(email))

    # We need to get the respondent to make sure they exist, but also because the id (not the party_uuid...for
    # some reason) of the respondent is needed for the later deletion steps.
    respondent = get_single_respondent_by_email(email, session)

    session.query(Enrolment).filter(Enrolment.respondent_id == respondent.id).delete()
    session.query(BusinessRespondent).filter(BusinessRespondent.respondent_id == respondent.id).delete()
    session.query(PendingEnrolment).filter(PendingEnrolment.respondent_id == respondent.id).delete()
    session.query(Respondent).filter(Respondent.email_address == email).delete()

    logger.info(
        "Deleted user, about to commit",
        email=obfuscate_email(email),
        party_uuid=str(respondent.party_uuid),
        id=respondent.id,
    )


@with_query_only_db_session
def get_respondent_by_email(email: str, session):
    """
    Get a verified respondent by its email address.
    Returns either the unique respondent identified by the supplied email address, or otherwise raises
    a RasError to indicate the email address doesn't exist.

    :param email: Email of respondent to lookup
    :rtype: Respondent
    """
    respondent = query_respondent_by_email(email, session)
    if not respondent:
        logger.info("Respondent does not exist")
        raise NotFound("Respondent does not exist")

    return respondent.to_respondent_dict()


@with_db_session
def change_respondent_details(respondent_data, respondent_id, session):
    """
    Completely replaces current respondent details with the data provided

    :param respondent_data: A dict containing all the respondent details
    :param respondent_id:
    :param session: A db session
    :return: None on success
    """

    respondent = query_respondent_by_party_uuid(respondent_id, session)
    if not respondent:
        logger.info("Respondent with party id does not exist", respondent_id=respondent_id)
        raise NotFound("Respondent id does not exist")

    # This function updates the name and number of a respondent
    update_respondent_details(respondent_data, respondent_id, session)

    if "new_email_address" in respondent_data:
        # This function only changes the respondents email address
        change_respondent(respondent_data)


def does_user_have_claim(user_id, business_id, survey_id):
    # with_db_session function wrapper automatically injects the session parameter
    # pylint: disable=no-value-for-parameter
    user_details = get_respondent_by_id(user_id)
    associations = user_details["associations"]
    is_enrolled = _is_user_enrolled_on_survey(associations, business_id, survey_id)
    return user_details["status"] == "ACTIVE" and is_enrolled


def _is_user_enrolled_on_survey(associations, business_id, survey_id):
    for association in associations:
        surveys = [v["surveyId"] for v in association["enrolments"] if v["enrolmentStatus"] == "ENABLED"]
        if survey_id in surveys and str(association["partyId"]) == business_id:
            return True

    return False
