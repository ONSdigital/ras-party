import connexion
from swagger_server.models.business import Business
from swagger_server.models.enrolment_code import EnrolmentCode
from swagger_server.models.enrolment_invitation import EnrolmentInvitation
from swagger_server.models.error import Error
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


def businesses_id_id_options(id):
    """
    View the available representations for a given Business
    
    :param id: ID of Business to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


def enrolment_codes_post(party=None):
    """
    redeems an Enrolment Code
    Redeems an Enrolment Code
    :param party: Enrolment Code to redeem
    :type party: dict | bytes

    :rtype: None
    """

    # TODO: see ras-party set_enrolment_code_as_redeemed_from_db

    if connexion.request.is_json:
        party = EnrolmentCode.from_dict(connexion.request.get_json())
    return 'do some magic!'


def enrolment_invitations_post(party=None):
    """
    stores an invitation to Enrol another Respondent to a Survey
    Stores an invitation to Enrol another Respondent to a Survey
    :param party: Enrolment Invitation to store
    :type party: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        party = EnrolmentInvitation.from_dict(connexion.request.get_json())
    return 'do some magic!'


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


def get_business_by_ref(ref):
    """
    Get a Business by its unique business reference
    Returns a single Business
    :param ref: Reference of the Business to return
    :type ref: str

    :rtype: Business
    """

    # TODO: see ras-party get-business-by-ref

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
