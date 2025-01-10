import logging

import requests
import structlog
from flask import current_app
from requests.exceptions import ConnectionError, HTTPError, Timeout

from ras_party.exceptions import ServiceUnavailableException

logger = structlog.wrap_logger(logging.getLogger(__name__))


def get_surveys_details() -> dict:
    url = f'{current_app.config["SURVEY_URL"]}/surveys'
    try:
        response = requests.get(
            url, auth=(current_app.config["SECURITY_USER_NAME"], current_app.config["SECURITY_USER_PASSWORD"])
        )
        response.raise_for_status()
    except HTTPError:
        logger.error("Survey returned a HTTPError")
        raise
    except ConnectionError:
        raise ServiceUnavailableException("Survey service returned a connection error", 503)
    except Timeout:
        raise ServiceUnavailableException("Survey service has timed out", 504)

    return {
        survey["id"]: {"short_name": survey["shortName"], "long_name": survey["longName"], "ref": survey["surveyRef"]}
        for survey in response.json()
    }
