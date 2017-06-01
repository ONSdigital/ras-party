
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
    attributes = party_data['attributes']

    party = Party(party_id)
    business = Business(attributes, party)

    db.session.merge(party)
    db.session.merge(business)
    db.session.commit()

    return make_response(jsonify("Ok, business entity created"), 201)


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
