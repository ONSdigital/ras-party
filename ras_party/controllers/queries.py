import logging

from sqlalchemy import func
import structlog

from ras_party.models.models import Business, Respondent

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
    logger.debug('Querying respondents by email', email=email)

    return session.query(Respondent).filter(func.lower(Respondent.email_address) == email.lower()).first()
