
#
# /businesses
#
from flask import make_response, jsonify

from swagger_server.configuration import ons_env
from swagger_server.models.model import Business, Party

db = ons_env


def businesses_post(party_data):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param party_data: Business to add
    :type party_data: dict | bytes

    :rtype: None
    """

    party_id = party_data['id']
    ru_ref = party_data['reference']
    attributes = party_data['attributes']

    party = db.session.query(Party).filter(party_id == party_id).first()
    if not party:
        party = Party(party_id)

    business = db.session.query(Business).filter(ru_ref == ru_ref).first()
    if not business:
        business = Business(ru_ref, attributes, party)
        db.session.add(business)

    db.session.commit()

    return make_response(jsonify("Ok, business entity created"), 200)


#
# /parties
#
def parties_post(party):
    """
    given a sampleUnitType B | H this adds a reporting unit of type Business or Household
    Adds a new Party of type sampleUnitType or updates an existing Party based on the reference provided
    :param party: Party to add
    :type party: dict | bytes

    :rtype: None
    """
    if 'sampleUnitType' not in party:
        return make_response(jsonify("sampleUnitType attribute is missing from the supplied JSON party."), 400)

    if party['sampleUnitType'] == 'B':
        return businesses_post(party)


#
# /parties/ref/{ref}
#
def get_party_by_ref(ref):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    return 'do some magic!'
