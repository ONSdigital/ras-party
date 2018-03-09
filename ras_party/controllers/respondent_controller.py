from ras_party.controllers.queries import query_respondent_by_party_uuid, query_respondent_by_email,\
    update_respondent_details
from ras_party.controllers.validate import Validator, IsUuid
from ras_party.exceptions import RasError
from ras_party.support.session_decorator import with_db_session


@with_db_session
def get_respondent_by_id(id, session):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    v = Validator(IsUuid('id'))
    if not v.validate({'id': id}):
        raise RasError(v.errors, status=400)

    respondent = query_respondent_by_party_uuid(id, session)
    if not respondent:
        raise RasError("Respondent with party id does not exist.", id=id, status=404)

    return respondent.to_respondent_dict()


@with_db_session
def get_respondent_by_email(email, session):
    """
    Get a respondent by its email address.
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
        raise RasError("Respondent id does not exist.", id=respondent_id, status=404)

    update_respondent_details(respondent_data, respondent_id, session)
