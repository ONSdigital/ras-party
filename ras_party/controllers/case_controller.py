import logging

import requests
import structlog
from flask import current_app

logger = structlog.wrap_logger(logging.getLogger(__name__))


def post_case_event(case_id: str, category="Default category message", desc="Default description message"):
    """Posts a case event

    :raises HTTPError: Raised if the post returns a failure status code
    """
    logger.info("Posting case event", case_id=case_id)
    case_svc = current_app.config["CASE_URL"]
    case_url = f"{case_svc}/cases/{case_id}/events"
    payload = {"description": desc, "category": category, "createdBy": "Party Service"}
    auth = (current_app.config["SECURITY_USER_NAME"], current_app.config["SECURITY_USER_PASSWORD"])

    response = requests.post(case_url, json=payload, auth=auth)
    response.raise_for_status()
    logger.info("Successfully posted case event", case_id=case_id)
    return response.json()


def get_cases_for_casegroup(case_group_id: str):
    logger.info("Requesting cases for case group", casegroup_id=case_group_id)
    case_svc = current_app.config["CASE_URL"]
    get_case_url = f"{case_svc}/cases/casegroupid/{case_group_id}"
    auth = (current_app.config["SECURITY_USER_NAME"], current_app.config["SECURITY_USER_PASSWORD"])
    response = requests.get(get_case_url, auth=auth)
    response.raise_for_status()
    logger.info("Successfully retrieved case for case group", casegroup_id=case_group_id)
    return response.json()
