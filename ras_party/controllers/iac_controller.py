import logging

import requests
import structlog

from flask import current_app

from ras_party.support.requests_wrapper import Requests

logger = structlog.wrap_logger(logging.getLogger(__name__))


def request_iac(enrolment_code):
    iac_svc = current_app.config['IAC_SERVICE']
    iac_url = f'{iac_svc}/iacs/{enrolment_code}'
    response = Requests.get(iac_url)
    response.raise_for_status()
    return response.json()


def disable_iac(enrolment_code, case_id):
    iac_svc = current_app.config['IAC_SERVICE']
    iac_url = f'{iac_svc}/iacs/{enrolment_code}'
    payload = {
        "updatedBy": "Party Service"
    }
    response = Requests.put(iac_url, json=payload)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.error("IAC failed to be disabled", case_id=case_id)
    return response.json()
