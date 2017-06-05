#
# /businesses
#
from flask import make_response, jsonify

from swagger_server.configuration import ons_env
from swagger_server.models_local.model import Business, Party

db = ons_env

"""
/businesses
	GET = businesses_get
	POST = businesses_post
/businesses/id/{id}
	GET = get_business_by_id
	OPTIONS = businesses_id_id_options
	PUT = businesses_id_id_put
/businesses/id/{id}/business-associations
	GET = businesses_id_id_business_associations_get
/businesses/ref/{ref}
	GET = get_business_by_ref
/enrolment-codes
	GET = enrolment_codes_get
	POST = enrolment_codes_post
/enrolment-invitations
	GET = enrolment_invitations_get
	POST = enrolment_invitations_post
/parties
	POST = parties_post
/parties/type/{sampleUnitType}/id/{id}
	GET = get_party_by_id
/parties/type/{sampleUnitType}/ref/{sampleUnitRef}
	GET = get_party_by_ref
/residences
	GET = residences_get
	POST = residences_post
/residences/id/{id}
	GET = get_residence_by_id
	OPTIONS = residences_id_id_options
	PUT = residences_id_id_put
/residences/uprn/{uprn}
	GET = get_residence_by_uprn
/respondents
	GET = respondents_get
	POST = respondents_post
/respondents/id/{id}
	GET = get_respondent_by_id
	OPTIONS = respondents_id_id_options
	PUT = respondents_id_id_put
/respondents/id/{id}/business-associations
	GET = respondents_id_id_business_associations_get
"""


def businesses_post(party_data):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param party_data: Business to add
    :type party_data: dict | bytes

    :rtype: None
    """

    # TODO: deal with missing id or reference
    party_uuid = party_data['id']
    ru_ref = party_data['reference']
    attributes = party_data.get('attributes', {})

    # TODO: validate received uuid

    party = db.session.query(Party).filter(Party.party_uuid == party_uuid).first()
    if not party:
        party = Party(party_uuid)

    business = db.session.query(Business).filter(Business.ru_ref == ru_ref).first()
    # TODO: update/replace the existing business attributes
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
def get_party_by_ref(sampleUnitType, sampleUnitRef):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """

    if sampleUnitType == 'B':
        return get_business_by_ref(sampleUnitRef)


#
# /parties/{id}
#
def get_party_by_id(sampleUnitType, id):
    return "Please implement me"


#
# /businesses/id/{id}
#
def businesses_id_id_put(id, binaryparty, ETag=None):
    """
    Update the representation for an existing Business
    Updates the representation for an existing Business
    :param id: ID of Party to update
    :type id: str
    :param binaryparty: Binary Party to add
    :type binaryparty: werkzeug.datastructures.FileStorage
    :param ETag: The current ETag value for the Party
    :type ETag: str

    :rtype: None
    """
    return 'do some magic!'


#
# /businesses/id/{id}/business-associations
#
def businesses_id_id_business_associations_get(id, skip=None, limit=None):
    """
    Returns the known business associations for a business
    Returns the known business associations for a business
    :param id: ID of Business to return
    :type id: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /enrolment-codes
#
def enrolment_codes_get(searchString=None, skip=None, limit=None):
    """
    searches enrolment codes
    By passing in the appropriate options, you can search for available Enrolment Codes
    :param searchString: pass an optional search string for looking up Enrolment Codes
    :type searchString: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /enrolment-invitations
#
def enrolment_invitations_get(searchString=None, skip=None, limit=None):
    """
    searches enrolment invitations
    By passing in the appropriate options, you can search for available Enrolment Invitations
    :param searchString: pass an optional search string for looking up Enrolment Invitations
    :type searchString: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /respondents
#
def respondents_get(searchString=None, skip=None, limit=None):
    """
    searches Respondents
    By passing in the appropriate options, you can search for available Respondentes
    :param searchString: pass an optional search string for looking up Respondents
    :type searchString: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /respondents/id/{id}
#
def get_respondent_by_id(id):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    return 'do some magic!'


#
# /respondents/id/{id}
#
def respondents_id_id_options(id):
    """
    View the available representations for a given Respondent

    :param id: ID of Respondent to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


#
# /respondents/id/{id}/business-associations
#
def respondents_id_id_business_associations_get(id, skip=None, limit=None):
    """
    Returns the known business associations for a respondent
    Returns the known business associations for a respondent
    :param id: ID of Respondent
    :type id: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /businesses
#
def businesses_get(searchString=None, skip=None, limit=None):
    """
    searches Businesses
    By passing in the appropriate options, you can search for available Businesses
    :param searchString: pass an optional search string for looking up Businesses
    :type searchString: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


#
# /businesses/ref/{ref}
#
def get_business_by_ref(ref):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """

    business = db.session.query(Business).filter(Business.ru_ref == ref).first()
    d = {
        'id': business.party.party_uuid,
        'reference': business.ru_ref,
        'sampleUnitType': 'B',
        'attributes': business.attributes
    }

    return make_response(jsonify(d), 200)


#
# /businesses/id/{id}
#
def get_business_by_id(id):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param id: ID of Party to return
    :type id: str

    :rtype: Business
    """

    # TODO: see ras-party get-business-by-id

    return 'do some magic!'


#
# /businesses/id/{id}
#
def businesses_id_id_options(id):
    """
    View the available representations for a given Business

    :param id: ID of Business to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


#
# /enrolment-codes
#
def enrolment_codes_post(party=None):
    """
    redeems an Enrolment Code
    Redeems an Enrolment Code
    :param party: Enrolment Code to redeem
    :type party: dict | bytes

    :rtype: None
    """
    return 'do some magic!'


#
# /enrolment-invitations
#
def enrolment_invitations_post(party=None):
    """
    stores an invitation to Enrol another Respondent to a Survey
    Stores an invitation to Enrol another Respondent to a Survey
    :param party: Enrolment Invitation to store
    :type party: dict | bytes

    :rtype: None
    """
    return 'do some magic!'


#
# /respondents/id/{id}
#
def respondents_id_id_put(id, ETag=None):
    """
    Update the representation for an existing Respondent.
    Updates the representation for an existing Respondent. To be used to activate a Respondent when their email address has been confirmed.
    :param id: ID of Respondent to update
    :type id: str
    :param ETag: The current ETag value for the Respondent
    :type ETag: str

    :rtype: None
    """
    return 'do some magic!'


#
# /respondents
#
def respondents_post(party=None):
    """
    adds a Respondent
    Adds a Respondent to the system
    :param party: Respondent to add
    :type party: dict | bytes

    :rtype: None
    """
    return 'do some magic!'


#
# /parties/uprn/{uprn}:
#
def get_party_by_uprn(urpn):
    return "Please implement me"


#
# /residences/id/{id}
#
def get_residence_by_id(id):
    return "Please implement me"


#
# /residences/id/{uprn}
#
def get_residence_by_uprn(uprn):
    return "Please implement me"


#
# /residences
#
def residences_id_id_put(residences_data):
    return "Please implement me"


def residences_id_id_options():
    return "Please implement me"


def residences_get(searchString, skip, limit):
    return "Please implement me"


def residences_post(residences_data):
    return "Please implement me"

