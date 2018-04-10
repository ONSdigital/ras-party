import logging

from sqlalchemy import func, and_, or_
import structlog

from ras_party.models.models import Business, BusinessRespondent, Enrolment, Respondent, BusinessAttributes

logger = structlog.wrap_logger(logging.getLogger(__name__))


def query_business_by_party_uuid(party_uuid, session):
    """
    Query to return business based on party uuid
    :param party_uuid: the party uuid
    :return: business or none
    """
    logger.debug('Querying businesses by party_uuid', party_uuid=party_uuid)

    return session.query(Business).filter(Business.party_uuid == party_uuid).first()


def query_business_by_ref(business_ref, session):
    """
    Query to return business based on business ref
    :param business_ref: the business ref
    :return: business or none
    """
    logger.debug('Querying businesses by business_ref', business_ref=business_ref)

    return session.query(Business).filter(Business.business_ref == business_ref).first()


def query_respondent_by_party_uuid(party_uuid, session):
    """
    Query to return respondent based on party uuid
    :param party_uuid: the party uuid
    :return: respondent or none
    """
    logger.debug('Querying respondents by party_uuid', party_uuid=party_uuid)

    return session.query(Respondent).filter(Respondent.party_uuid == party_uuid).first()


def query_respondent_by_email(email, session):
    """
    Query to return respondent based on email
    :param email: the party uuid
    :return: respondent or none
    """
    logger.debug('Querying respondents by email')

    return session.query(Respondent).filter(func.lower(Respondent.email_address) == email.lower()).first()


def query_respondent_by_email_filter_out_created(email, session):
    """
    Query to return respondent based on email
    :param email: the party uuid
    :return: respondent or none
    """
    logger.debug('Querying respondents by email')

    return session.query(Respondent).filter(and_(func.lower(Respondent.email_address) == email.lower(),
                                                 Respondent.status != 'CREATED')).first()


def query_business_respondent_by_respondent_id_and_business_id(business_id, respondent_id, session):
    """
    Query to return respondent business associations based on respondent id
    :param business_id,
    :param respondent_id,
    :param session
    :return: business associations for respondent
    """
    logger.debug('Querying business respondent', respondent_id=respondent_id)

    response = session.query(BusinessRespondent).filter(and_(BusinessRespondent.business_id == business_id,
                                                             BusinessRespondent.respondent_id == respondent_id)).first()
    return response


def update_respondent_details(respondent_data, respondent_id, session):
    """
    Query to return respondent, respondent_data consists of the following parameters
    :param respondent_data:
        respondent_id: id of the respondent
        first_name:
        last_name:
        telephone:
    :param session
    """

    logger.debug('Updating respondent details', respondent_id=respondent_id)

    respondent_details = query_respondent_by_party_uuid(respondent_id, session)

    if respondent_details.first_name != respondent_data['firstName'] or respondent_details.last_name != \
            respondent_data['lastName'] or respondent_details.telephone != respondent_data['telephone']:

        session.query(Respondent).filter(Respondent.party_uuid == respondent_id).update({
                                         Respondent.first_name: respondent_data['firstName'],
                                         Respondent.last_name: respondent_data['lastName'],
                                         Respondent.telephone: respondent_data['telephone']})

        return True
    return False


def search_businesses(search_query, session):
    """
    Query to return list of businesses based on search query
    :param search_query: the search query
    :return: list of businesses
    """
    logger.debug('Searching businesses by name with search query', search_query=search_query)
    filters = list()
    name_filters = list()

    key_words = search_query.split()

    for word in key_words:
        name_filters.append(BusinessAttributes.attributes['name'].astext.ilike(f'%{word}%'))

    filters.append(Business.business_ref.ilike(f'%{search_query}%'))
    filters.append(and_(*name_filters))

    return session.query(BusinessAttributes.attributes['name'], Business.business_ref).join(Business)\
        .filter(or_(*filters)).distinct().all()


def query_enrolment_by_survey_business_respondent(respondent_id, business_id, survey_id, session):
    """
    Query to return enrolment based on respondent id, business id and survey
    :param respondent_id,
    :param business_id,
    :param survey_id
    :return: enrolment for survey and business for respondent
    """

    logger.debug('Querying enrolment', respondent_id=respondent_id, business_id=business_id, survey_id=survey_id)

    response = session.query(Enrolment).filter(and_(Enrolment.respondent_id == respondent_id,
                                                    Enrolment.business_id == business_id,
                                                    Enrolment.survey_id == survey_id)).first()
    return response


def query_change_all_respondent_enrolments_to_disabled(respondent_party_id, session):
    """
    Query to update all respondent enrolments to disabled upon account suspension
    :param respondent_party_id, 
    :param session, 
    :return: 
    """

    logger.debug('Disabling respondent enrolments', party_id=respondent_party_id)

    respondent_db_id = session.query(Respondent).filter(Respondent.party_uuid == respondent_party_id).first()

    session.query(Enrolment).filter(Enrolment.respondent_id == respondent_db_id).update({
                                    Enrolment.status: 'DISABLED'})
