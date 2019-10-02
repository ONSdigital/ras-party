import logging
import uuid

import structlog
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers.account_controller import change_respondent
from ras_party.models.models import Enrolment, BusinessRespondent, PendingEnrolment, Respondent
from ras_party.controllers.queries import query_respondent_by_party_uuid, \
    query_respondent_by_email, update_respondent_details, query_respondent_by_names_and_emails, \
    query_respondent_by_party_uuids
from ras_party.support.session_decorator import with_db_session


logger = structlog.wrap_logger(logging.getLogger(__name__))


@with_db_session
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


@with_db_session
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
    return {'data': [respondent.to_respondent_dict() for respondent in respondents], 'total': record_count}


@with_db_session
def get_respondent_by_id(respondent_id, session):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param respondent_id: ID of Respondent to return
    :type respondent_id: str

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
def delete_respondent_by_id(party_uuid, session):
    """
    Delete a Respondent by its Party ID
    On success it returns None, on failure will raise one of many different exceptions
    :param party_uuid: Id of Respondent to delete
    :type party_uuid: str
    """
    logger.info("Starting to delete respondent", party_uuid=party_uuid)
    try:
        uuid.UUID(party_uuid)
    except ValueError:
        logger.info("party_uuid value is not a valid UUID", party_uuid=party_uuid)
        raise BadRequest(f"'{party_uuid}' is not a valid UUID format for property 'party_uuid'")

    # We need to get the respondent to make sure they exist, but also because the id (not the party_uuid...for
    # some reason) of the respondent is needed for the later deletion steps.
    respondent = query_respondent_by_party_uuid(party_uuid, session)
    if not respondent:
        logger.info("Respondent with party_uuid does not exist", party_uuid=party_uuid)
        raise NotFound("Respondent with party_uuid does not exist")

    logger.info("Found respondent", party_uuid=str(respondent.party_uuid), id=respondent.id)

    session.query(Enrolment).filter(Enrolment.respondent_id == respondent.id).delete()
    session.query(BusinessRespondent).filter(BusinessRespondent.respondent_id == respondent.id).delete()
    session.query(PendingEnrolment).filter(PendingEnrolment.respondent_id == respondent.id).delete()
    session.query(Respondent).filter(Respondent.party_uuid == party_uuid).delete()

    logger.info("Deleted user, about to commit", party_uuid=str(respondent.party_uuid), id=respondent.id)


@with_db_session
def get_respondent_by_email(email, session):
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
    :param respondent_data:
    :param respondent_id
    :param session:
    :return:
    """

    respondent = query_respondent_by_party_uuid(respondent_id, session)
    if not respondent:
        logger.info("Respondent with party id does not exist", respondent_id=respondent_id)
        raise NotFound("Respondent id does not exist")

    # This function updates the name and number of a respondent
    update_respondent_details(respondent_data, respondent_id, session)

    # This function only changes the respondents email address
    change_respondent(respondent_data)


def does_user_have_claim(user_id, business_id, survey_id):
    # with_db_session function wrapper automatically injects the session parameter
    # pylint: disable=no-value-for-parameter
    user_details = get_respondent_by_id(user_id)
    associations = user_details['associations']
    is_enrolled = _is_user_enrolled_on_survey(associations, business_id, survey_id)
    return user_details['status'] == 'ACTIVE' and is_enrolled


def _is_user_enrolled_on_survey(associations, business_id, survey_id):
    for association in associations:
        surveys = [v['surveyId'] for v in association['enrolments'] if v['enrolmentStatus'] == 'ENABLED']
        if survey_id in surveys and str(association['partyId']) == business_id:
            return True

    return False
