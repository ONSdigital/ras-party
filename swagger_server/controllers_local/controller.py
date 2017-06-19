#
# /businesses
#
import uuid

from flask import make_response, jsonify
from ons_ras_common import ons_env

from swagger_server.controllers_local.session_context import transaction
from swagger_server.controllers_local.error_decorator import convert_exceptions
from swagger_server.controllers_local.validate import Validator, Exists, IsUuid, IsIn
from swagger_server.models.models import Business, Party, Respondent, BusinessRespondent


db = ons_env.db


@convert_exceptions
def businesses_post(business):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param business: Business to add
    :type business: dict | bytes

    :rtype: None
    """

    with transaction() as tran:
        v = Validator(Exists('businessRef',
                             'attributes',
                             'attributes.contactName',
                             'attributes.employeeCount',
                             'attributes.enterpriseName',
                             'attributes.enterpriseName',
                             'attributes.facsimile',
                             'attributes.fulltimeCount',
                             'attributes.legalStatus',
                             'attributes.name',
                             'attributes.sic2003',
                             'attributes.sic2007',
                             'attributes.telephone',
                             'attributes.tradingName',
                             'attributes.turnover'
                             ))
        if 'id' in business:
            v.add_rule(IsUuid('id'))
        if not v.validate(business):
            return make_response(jsonify(v.errors), 400)

        party_uuid = business.get('id', uuid.uuid4())
        business_ref = business['businessRef']
        associations = business.get('associations')

        db_party = tran.query(Party).filter(Party.party_uuid == party_uuid).first()

        if db_party and not db_party.business:
            return make_response(jsonify({'errors': "Existing party with '{}' does not identify a business."
                                         .format(party_uuid)}), 400)

        if db_party:
            db_business = db_party.business
        else:
            db_party = Party(party_uuid)
            db_business = Business(business_ref, db_party)
            tran.add(db_business)

        db_business.from_dict(business['attributes'])

        if associations:
            for assoc in associations:
                assoc_id = assoc['id']

                assoc_party = tran.query(Party).filter(Party.party_uuid == assoc_id).first()
                business_respondent = BusinessRespondent()
                business_respondent.respondent = assoc_party.respondent
                business_respondent.business = db_business
                # TODO: check the association doesn't already exist?
                tran.add(business_respondent)

        return make_response(jsonify(db_business.to_dict()), 200)


@convert_exceptions
def get_business_by_ref(ref):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """

    business = db.session.query(Business).filter(Business.business_ref == ref).first()
    if not business:
        return make_response(jsonify({'errors': "Business with reference '{}' does not exist.".format(ref)}), 404)

    return make_response(jsonify(business.to_dict()), 200)


@convert_exceptions
def get_business_by_id(id):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param id: ID of Party to return
    :type id: str

    :rtype: Business
    """

    v = Validator(IsUuid('id'))
    if not v.validate({'id': id}):
        return make_response(jsonify(v.errors), 400)

    party = db.session.query(Party).filter(Party.party_uuid == id).first()
    if not party:
        return make_response(jsonify({'errors': "Business with party id '{}' does not exist.".format(id)}), 404)
    if not party.business:
        return make_response(jsonify({'errors': "Party id '{}' is not associated with a business.".format(id)}), 404)

    return make_response(jsonify(party.business.to_dict()), 200)


@convert_exceptions
def parties_post(party):
    """
    given a sampleUnitType B | H this adds a reporting unit of type Business or Household
    Adds a new Party of type sampleUnitType or updates an existing Party based on the reference provided
    :param party: Party to add
    :type party: dict | bytes

    :rtype: None
    """

    v = Validator(Exists('sampleUnitType'), IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate(party):
        return make_response(jsonify(v.errors), 400)

    if party['sampleUnitType'] == Business.UNIT_TYPE:
        return businesses_post(party)
    elif party['sampleUnitType'] == Respondent.UNIT_TYPE:
        return respondents_post(party)


@convert_exceptions
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sampleUnitType}):
        return make_response(jsonify(v.errors), 400)

    if sampleUnitType == Business.UNIT_TYPE:
        return get_business_by_ref(sampleUnitRef)


@convert_exceptions
def get_party_by_id(sampleUnitType, id):
    v = Validator(IsIn('sampleUnitType', 'B', 'BI'))
    if not v.validate({'sampleUnitType': sampleUnitType}):
        return make_response(jsonify(v.errors), 400)

    if sampleUnitType == Business.UNIT_TYPE:
        return get_business_by_id(id)
    elif sampleUnitType == Respondent.UNIT_TYPE:
        return get_respondent_by_id(id)


@convert_exceptions
def get_respondent_by_id(id):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """

    v = Validator(IsUuid('id'))
    if not v.validate({'id': id}):
        return make_response(jsonify(v.errors), 400)

    party = db.session.query(Party).filter(Party.party_uuid == id).first()
    if not party:
        return make_response(jsonify({'errors': "Respondent with party id '{}' does not exist.".format(id)}), 404)
    if not party.respondent:
        return make_response(jsonify({'errors': "Party id '{}' is not associated with a respondent.".format(id)}), 404)

    return make_response(jsonify(party.respondent.to_dict()), 200)


@convert_exceptions
def respondents_post(party):
    """
    adds a Respondent
    Adds a Respondent to the system
    :param party: Respondent to add
    :type party: dict | bytes

    :rtype: None
    """

    with transaction() as tran:
        v = Validator(Exists('emailAddress', 'firstName', 'lastName', 'telephone'))
        if 'id' in party:
            v.add_rule(IsUuid('id'))
        if not v.validate(party):
            return make_response(jsonify(v.errors), 400)

        party_uuid = party.get('id', uuid.uuid4())
        db_party = tran.query(Party).filter(Party.party_uuid == party_uuid).first()

        if db_party and not db_party.respondent:
            return make_response(jsonify({'errors': "Existing party with '{}' does not identify a respondent."
                                         .format(party_uuid)}), 400)

        if not db_party:
            db_party = Party(party_uuid)
            respondent = Respondent(db_party)
            tran.add(respondent)
        else:
            respondent = db_party.respondent

        respondent.email_address = party['emailAddress']
        respondent.first_name = party['firstName']
        respondent.last_name = party['lastName']
        respondent.telephone = party['telephone']

        return make_response(jsonify(respondent.to_dict()), 200)
