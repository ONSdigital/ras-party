import logging

import structlog
from flask import current_app

from ras_party.support.requests_wrapper import Requests

logger = structlog.wrap_logger(logging.getLogger(__name__))


def post_case_event(case_id, category="Default category message", desc="Default description message"):
    """Posts a case event

    :raises HTTPError: Raised if the post returns a failure status code
    """
    logger.info("Posting case event", case_id=case_id)
    case_svc = current_app.config["CASE_URL"]
    case_url = f"{case_svc}/cases/{case_id}/events"
    payload = {"description": desc, "category": category, "createdBy": "Party Service"}

    response = Requests.post(case_url, json=payload)
    response.raise_for_status()
    logger.info("Successfully posted case event", case_id=case_id)
    return response.json()


def get_cases_for_casegroup(case_group_id):
    logger.info("Requesting cases for case group", casegroup_id=case_group_id)
    case_svc = current_app.config["CASE_URL"]
    get_case_url = f"{case_svc}/cases/casegroupid/{case_group_id}"

    response = Requests.get(get_case_url)
    response.raise_for_status()
    logger.info("Successfully retrieved case for case group", casegroup_id=case_group_id)
    return response.json()
