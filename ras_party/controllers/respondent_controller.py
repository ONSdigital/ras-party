import uuid

from ras_party.controllers.queries import query_respondent_by_party_uuid, \
    query_respondent_by_email, update_respondent_details, query_respondent_by_party_uuids

from ras_party.exceptions import RasError
from ras_party.support.session_decorator import with_db_session
from ras_party.controllers.account_controller import change_respondent


@with_db_session
def get_respondent_by_ids(ids, session):
    """
    Get respondents by Party IDs, if an id doesn't exist then nothing is return for that id.
    Returns multiple parties
    :param ids: the ids of Respondent to return
    :type ids: str

    :rtype: Respondent
    """
    for party_id in ids:
        try:
            uuid.UUID(party_id)
        except ValueError:
            raise RasError(f"'{party_id}' is not a valid UUID format for property 'id'.", status=400)

    respondents = query_respondent_by_party_uuids(ids, session)
    return [respondent.to_respondent_dict() for respondent in respondents]


@with_db_session
def get_respondent_by_id(id, session):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    try:
        uuid.UUID(id)
    except ValueError:
        raise RasError(f"'{id}' is not a valid UUID format for property 'id'.", status=400)

    respondent = query_respondent_by_party_uuid(id, session)
    if not respondent:
        raise RasError("Respondent with party id does not exist.", respondent_id=id, status=404)

    return respondent.to_respondent_dict()


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
        raise RasError("Respondent does not exist.", status=404)

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
        raise RasError("Respondent id does not exist.", respondent_id=respondent_id, status=404)

    # This function updates the name and number of a respondent
    update_respondent_details(respondent_data, respondent_id, session)

    # This function only changes the respondents email address
    change_respondent(respondent_data)
