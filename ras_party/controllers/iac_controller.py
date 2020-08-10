import logging

import requests
import structlog

from flask import current_app

from ras_party.support.requests_wrapper import Requests

logger = structlog.wrap_logger(logging.getLogger(__name__))


def request_iac(enrolment_code):
    iac_url = f'{current_app.config["IAC_URL"]}/iacs/{enrolment_code}'
    response = Requests.get(iac_url)
    response.raise_for_status()
    return response.json()


def disable_iac(enrolment_code, case_id):
    """
    Disables the iac code by calling the iac service
    :param enrolment_code: A string containing the code to disable
    :param case_id: A string containing a uuid for the case
    :returns:  A dictionary containing the json response from the call
    :raises ValueError:  Raised when the response doesn't return json (on a 500 response?)
    """
    iac_url = f'{current_app.config["IAC_URL"]}/iacs/{enrolment_code}'
    payload = {
        "updatedBy": "Party Service"
    }
    response = Requests.put(iac_url, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        # Needs to be investigated by someone with more time, do we swallow the HTTPError because the
        # response.json line below will probably throw a ValueError?  If it's a 404 then it's assumed that
        # it returns a json message saying it's not found.  Or is the idea to not interrupt the users
        # journey and we can just handle it ourselves after the fact?
        logger.error("IAC failed to be disabled", case_id=case_id)

    return response.json()
