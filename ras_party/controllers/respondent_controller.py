import logging
import uuid
from uuid import UUID

import structlog
from flask import current_app, session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers.account_controller import (
    change_respondent,
    get_single_respondent_by_email,
)
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.queries import (
    query_enrolment_by_survey_business_respondent,
    query_respondent_by_email,
    query_respondent_by_names_and_emails,
    query_respondent_by_party_uuid,
    query_respondent_by_party_uuids,
    query_respondents_and_status_by_survey_and_business_id,
    update_respondent_details,
)
from ras_party.models.models import (
    BusinessRespondent,
    Enrolment,
    PendingEnrolment,
    Respondent,
    RespondentStatus,
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
    return [respondent.to_respondent_with_associations_dict() for respondent in respondents]


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
    return {
        "data": [respondent.to_respondent_with_associations_dict() for respondent in respondents],
        "total": record_count,
    }


@with_query_only_db_session
def get_respondent_by_party_id(party_id: UUID, session:session) -> Respondent:
    return query_respondent_by_party_uuid(party_id, session)


@with_query_only_db_session
def get_respondent_by_id(respondent_id, session):
    """
    Get a Respondent by its Party ID.

    :param respondent_id: ID of Respondent to return
    :type respondent_id: str
    :return: An object representing a respondent, if it exists.
    :rtype: respondent dict with business associations
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

    return respondent.to_respondent_with_associations_dict()


@with_db_session
def update_respondent_mark_for_deletion(email: str, session):
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
        send_account_deletion_confirmation_email(respondent.email_address, respondent.first_name)


def send_account_deletion_confirmation_email(email_address: str, name: str):
    """
    Sends email notification for account deletion confirmation.
    """
    bound_logger = logger.bind(email=obfuscate_email(email_address))
    bound_logger.info("sending account deletion confirmation email")
    try:
        personalisation = {"name": name}
        NotifyGateway(current_app.config).request_to_notify(
            email=email_address, template_name="account_deletion_confirmation", personalisation=personalisation
        )
        bound_logger.info("account deletion confirmation email sent successfully")
    # Exception is used to abide by the notify controller. At this point of time the respondent has been deleted
    # hence if the email phase fails it should not disrupt the flow.
    except Exception as e:  # noqa
        bound_logger.error("Error sending confirmation email for account deletion")


@with_db_session
def delete_respondent_by_email(email: str, session):
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

    return respondent.to_respondent_with_associations_dict()


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


@with_db_session
def get_respondents_by_survey_and_business_id(survey_id: UUID, business_id: UUID, session: session) -> list:
    """
    Gets a list of Respondents enrolled in a survey for a specified business

    :param survey_id: the survey UUID
    :param business_id: the business UUID
    :param session: A db session
    :return: list of respondents
    """

    respondents_and_status = query_respondents_and_status_by_survey_and_business_id(survey_id, business_id, session)

    respondents_enrolled = []
    for respondent, status in respondents_and_status:
        respondents_enrolled.append(
            {
                "respondent": respondent.to_respondent_dict(),
                "enrolment_status": status.name,
            }
        )

    return respondents_enrolled


@with_query_only_db_session
def is_user_enrolled(party_uuid: UUID, business_id: UUID, survey_id: UUID, session: session) -> bool:
    respondent = query_respondent_by_party_uuid(party_uuid, session)

    if respondent and respondent.status == RespondentStatus.ACTIVE:
        enrolment = query_enrolment_by_survey_business_respondent(respondent.id, business_id, survey_id, session)
        if enrolment:
            return True
    return False
