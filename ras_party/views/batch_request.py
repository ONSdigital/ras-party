import json
import logging

import structlog
from flask import Blueprint, current_app, make_response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import abort

from ras_party.controllers import pending_survey_controller, respondent_controller
from ras_party.controllers.pending_survey_controller import get_unique_pending_surveys
from ras_party.controllers.respondent_controller import get_respondent_by_id
from ras_party.support.public_website import PublicWebsite
from ras_party.views.pending_survey_view import send_pending_survey_email

logger = structlog.wrap_logger(logging.getLogger(__name__))
batch_request = Blueprint("batch_request", __name__)
auth = HTTPBasicAuth()


@batch_request.before_request
@auth.login_required
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password


@batch_request.route("/batch/respondents", methods=["DELETE"])
def delete_user_data_marked_for_deletion():
    """
    Endpoint Exposed for Kubernetes Cronjob to delete all respondents and
    its associated data marked for deletion
    """
    respondent_controller.delete_respondents_marked_for_deletion()
    return "", 204


@batch_request.route("/batch/requests", methods=["POST"])
def batch():
    """
    Execute multiple requests, submitted as a batch.
    :status code 207: Multi status
    :response body: Individual request status code
    Batch Request data Example:
    [
        {
            "method": "PATCH",
            "path": "/party-api/v1/respondents/email",
            "body": respondent_email_3,
            "headers": <headers>
        },
        {
            "method": "PATCH",
            "path": "/party-api/v1/respondents/email",
            "body": respondent_email_0,
            "headers": <headers>
        },
    ]
    """
    try:
        requests = json.loads(request.data)
    except ValueError:
        abort(400)

    responses = []

    for index, req in enumerate(requests):
        method = req["method"]
        path = req["path"]
        body = req.get("body", None)
        headers = req.get("headers", None)

        with current_app.app_context():
            with current_app.test_request_context(path, method=method, json=body, headers=headers):
                try:
                    rv = current_app.preprocess_request()
                    if rv is None:
                        rv = current_app.dispatch_request()
                except Exception as e:
                    rv = current_app.handle_user_exception(e)
                response = current_app.make_response(rv)
                response = current_app.process_response(response)
        responses.append(
            {
                "status": response.status_code,
            }
        )

    return make_response(json.dumps(responses), 207)


@batch_request.route("/batch/pending-surveys", methods=["DELETE"])
def delete_pending_surveys_deletion():
    """
    Endpoint Exposed for Kubernetes Cronjob to delete expired pending surveys
    """
    logger.info("Attempting to delete expired pending shares")
    unique_pending_share_surveys_to_be_emailed = get_unique_pending_surveys(False)
    unique_pending_transfer_surveys_to_be_emailed = get_unique_pending_surveys(True)
    pending_survey_controller.delete_pending_surveys()
    if len(unique_pending_share_surveys_to_be_emailed) > 0:
        logger.info(
            "number of share surveys cancellation emails to be sent",
            count=len(unique_pending_share_surveys_to_be_emailed),
        )
        send_share_survey_cancellation_emails(unique_pending_share_surveys_to_be_emailed)
    if len(unique_pending_transfer_surveys_to_be_emailed) > 0:
        logger.info(
            "number of transfer surveys cancellation emails to be sent",
            count=len(unique_pending_transfer_surveys_to_be_emailed),
        )
        send_transfer_survey_cancellation_emails(unique_pending_transfer_surveys_to_be_emailed)
    return "", 204


def send_share_survey_cancellation_emails(unique_pending_share_to_be_emailed: list):
    """
    sends pending share survey cancellation email
    :param unique_pending_share_to_be_emailed list of unique pending share record
    """
    logger.info("sending share survey cancellation emails")
    for data in unique_pending_share_to_be_emailed:
        respondent = get_respondent_by_id(str(data["shared_by"]))
        logger.info("sending share survey cancellation email", respondent=str(respondent["id"]))
        verification_url = PublicWebsite().resend_share_survey(data["batch_no"])
        personalisation = {
            "RESEND_EMAIL_URL": verification_url,
            "COLLEAGUE_EMAIL_ADDRESS": data["email_address"],
            "NAME": respondent["firstName"],
        }
        send_pending_survey_email(
            personalisation, "share_survey_access_cancellation", respondent["emailAddress"], data["batch_no"]
        )
        logger.info("share survey cancellation email send successfully", respondent=str(respondent["id"]))
    logger.info("share survey cancellation emails send successfully")


def send_transfer_survey_cancellation_emails(unique_pending_transfer_to_be_emailed: list):
    """
    sends pending transfer survey cancellation email
    :param unique_pending_transfer_to_be_emailed list of unique pending transfer record
    """
    logger.info("sending transfer survey cancellation emails")
    for data in unique_pending_transfer_to_be_emailed:
        respondent = get_respondent_by_id(str(data["shared_by"]))
        logger.info("sending transfer survey cancellation email", respondent=str(respondent["id"]))
        verification_url = PublicWebsite().resend_transfer_survey(data["batch_no"])
        personalisation = {
            "RESEND_EMAIL_URL": verification_url,
            "COLLEAGUE_EMAIL_ADDRESS": data["email_address"],
            "NAME": respondent["firstName"],
        }
        send_pending_survey_email(
            personalisation, "transfer_survey_access_cancellation", respondent["emailAddress"], data["batch_no"]
        )
        logger.info("transfer survey cancellation email send successfully", respondent=str(respondent["id"]))
    logger.info("transfer survey cancellation emails send successfully")
