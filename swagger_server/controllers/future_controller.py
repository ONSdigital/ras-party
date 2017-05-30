import connexion
from swagger_server.models.residence import Residence
from swagger_server.models.vnd_collectionjson import VndCollectionjson
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def get_residence_by_id(id):
    """
    Get a Residence by its Party ID
    Returns a single Party
    :param id: ID of Party to return
    :type id: str

    :rtype: Residence
    """
    return 'do some magic!'


def get_residence_by_uprn(uprn):
    """
    Get a Residence by its unique property reference
    Returns a single Residence
    :param uprn: Unique property reference of the Residence to return
    :type uprn: str

    :rtype: Residence
    """
    return 'do some magic!'


def residences_get(searchString=None, skip=None, limit=None):
    """
    searches Residences
    By passing in the appropriate options, you can search for available Residences 
    :param searchString: pass an optional search string for looking up Residences
    :type searchString: str
    :param skip: number of records to skip for pagination
    :type skip: int
    :param limit: maximum number of records to return
    :type limit: int

    :rtype: None
    """
    return 'do some magic!'


def residences_id_id_options(id):
    """
    View the available representations for a given Residence
    
    :param id: ID of Residence to return
    :type id: str

    :rtype: VndCollectionjson
    """
    return 'do some magic!'


def residences_id_id_put(id, binaryparty, ETag=None):
    """
    Update the representation for an existing Residence
    Updates the representation for an existing Residence
    :param id: ID of Party to update
    :type id: str
    :param binaryparty: Binary Party to add
    :type binaryparty: werkzeug.datastructures.FileStorage
    :param ETag: The current ETag value for the Party
    :type ETag: str

    :rtype: None
    """
    return 'do some magic!'


def residences_post(party=None):
    """
    adds a reporting unit of type Residence
    Adds a Residence to the system
    :param party: Residence to add
    :type party: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        party = Residence.from_dict(connexion.request.get_json())
    return 'do some magic!'
