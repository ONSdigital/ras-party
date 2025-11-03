from ras_party.controllers.queries import query_latest_business_name_ref
from ras_party.support.session_decorator import (
    with_db_session,
    with_query_only_db_session,
)
from ras_party.controllers.queries import (
    query_respondent_by_party_uuids,
    query_latest_business_name_ref
)


@with_query_only_db_session
def get_respondent_by_ids(ids, session):
    """
    Get respondents by Party IDs, if an id doesn't exist then nothing is return for that id.
    Returns multiple parties

    :param ids: the ids of Respondent to return
    :type ids: str
    :rtype: Respondent
    """



    test = {"respondent_details":[], "business_details":[]}
    respondent_details = query_respondent_by_party_uuids(ids["party_id"], session)
    business_details = query_latest_business_name_ref(session, ids["business_id"])

    for respondent in respondent_details:
        test["respondent_details"].append({"id":respondent.party_uuid, "name": f"{respondent.first_name} {respondent.last_name}"})

    for business in business_details:
        test["business_details"].append(
            {"id": business.party_uuid, "ru_ref": business.business_ref, "name": business.name})
    return test




