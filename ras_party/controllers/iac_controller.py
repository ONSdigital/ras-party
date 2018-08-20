from flask import current_app

from ras_party.support.requests_wrapper import Requests


def request_iac(enrolment_code):
    iac_svc = current_app.config['RAS_IAC_SERVICE']
    iac_url = f'{iac_svc}/iacs/{enrolment_code}'
    response = Requests.get(iac_url)
    response.raise_for_status()
    return response.json()


def disable_iac(enrolment_code):
    iac_svc = current_app.config['RAS_IAC_SERVICE']
    iac_url = f'{iac_svc}/iacs/{enrolment_code}'
    payload = {
        "updatedBy": "Party Service"
    }
    response = Requests.put(iac_url, json=payload)
    response.raise_for_status()
    return response.json()
