import connexion
from swagger_server.models.business import Business
from swagger_server.models.error import Error
from swagger_server.models.party import Party
from swagger_server.models.respondent import Respondent
from swagger_server.models.vnd_collectionjson import VndCollectionjson
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


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


def businesses_id_id_options(id):
    """
    View the available representations for a given Business
    
    :param id: ID of Business to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


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


def businesses_post(party=None):
    """
    adds a reporting unit of type Business
    Adds a new Business, or updates an existing Business based on the business reference provided
    :param party: Business to add
    :type party: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        party = Party.from_dict(connexion.request.get_json())
    return 'do some magic!'


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


def get_business_by_id(id):
    """
    Get a Business by its Party ID
    Returns a single Party
    :param id: ID of Party to return
    :type id: str

    :rtype: Business
    """
    return 'do some magic!'


def get_business_by_ref(ref):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """
    return 'do some magic!'


def get_party_by_ref(ref):
    """
    Get a Party by its unique reference (ruref / uprn)
    Returns a single Party
    :param ref: Reference of the Party to return
    :type ref: str

    :rtype: Party
    """
    return 'do some magic!'


def get_respondent_by_id(id):
    """
    Get a Respondent by its Party ID
    Returns a single Party
    :param id: ID of Respondent to return
    :type id: str

    :rtype: Respondent
    """
    return 'do some magic!'


def parties_post(party=None):
    """
    given a sampleUnitType B | H this adds a reporting unit of type Business or Household
    Adds a new Party of type sampleUnitType or updates an existing Party based on the reference provided
    :param party: Party to add
    :type party: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        party = Party.from_dict(connexion.request.get_json())
    return 'do some magic!'


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


def respondents_id_id_options(id):
    """
    View the available representations for a given Respondent
    
    :param id: ID of Respondent to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


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


def respondents_post(party=None):
    """
    adds a Respondent
    Adds a Respondent to the system
    :param party: Respondent to add
    :type party: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        party = Respondent.from_dict(connexion.request.get_json())
    return 'do some magic!'
