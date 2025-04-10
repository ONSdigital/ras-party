import logging
import uuid

import structlog
from flask import Blueprint, current_app, jsonify, make_response, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers import pending_survey_controller
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.pending_survey_controller import (
    confirm_pending_survey,
    get_pending_survey_by_batch_number,
    get_pending_survey_by_originator_respondent_id,
    pending_survey_deletion,
)
from ras_party.controllers.respondent_controller import (
    get_respondent_by_email,
    get_respondent_by_party_id,
)
from ras_party.controllers.validate import Exists, Validator
from ras_party.exceptions import RasNotifyError
from ras_party.support.public_website import PublicWebsite
from ras_party.views.account_view import auth

pending_survey_view = Blueprint("pending_survey_view", __name__)
logger = structlog.wrap_logger(logging.getLogger(__name__))


@pending_survey_view.before_request
@auth.login_required
def before_pending_survey_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password


@pending_survey_view.route("/pending-survey-users-count", methods=["GET"])
def pending_survey_users():
    """
    Get total users count who are already enrolled and pending transfer survey against business id and survey id
    """
    business_id = request.args.get("business_id")
    survey_id = request.args.get("survey_id")
    is_transfer = request.args.get("is_transfer", False)
    if business_id and survey_id:
        # this is just to validate that the business_id exists
        get_business_by_id(business_id)
        response = pending_survey_controller.get_users_enrolled_and_pending_survey_against_business_and_survey(
            business_id=business_id, survey_id=survey_id, is_transfer=is_transfer
        )
        return make_response(jsonify(response), 200)
    else:
        raise BadRequest("Business id and Survey id is required for this request.")


@pending_survey_view.route("/pending-surveys", methods=["POST"])
def post_pending_surveys():
    """
    Creates new records for share survey
    accepted payload example:
    {  pending_shares: [{
           "business_id": "business_id"
           "survey_id": "survey_id",
           "email_address": "email_address",
           "shared_by": "respondent_id"
       },
       {
           "business_id": "business_id":
           "survey_id": "survey_id",
           "email_address": "email_address",
           "shared_by": "respondent_id"
       }]
    }
    Creates new records for transfer surveys
    accepted payload example:
    {  pending_transfers: [{
           "business_id": "business_id"
           "survey_id": "survey_id",
           "email_address": "email_address",
           "shared_by": "respondent_id"
       },
       {
           "business_id": "business_id":
           "survey_id": "survey_id",
           "email_address": "email_address",
           "shared_by": "respondent_id"
       }]
    }
    """
    payload = request.get_json() or {}
    if "pending_shares" not in payload and "pending_transfers" not in payload:
        raise BadRequest("Payload Invalid - Pending survey key missing")
    if "pending_shares" in payload:
        is_transfer = False
        pending_surveys = payload["pending_shares"]
        existing_user_email_template = "share_survey_access_existing_account"
        new_user_email_template = "share_survey_access_new_account"
    else:
        is_transfer = True
        pending_surveys = payload["pending_transfers"]
        existing_user_email_template = "transfer_survey_access_existing_account"
        new_user_email_template = "transfer_survey_access_new_account"

    business_list = []
    if len(pending_surveys) == 0:
        raise BadRequest("Payload Invalid - pending_surveys list is empty")
    for survey in pending_surveys:
        # Validation, curation and checks
        expected = ("email_address", "survey_id", "business_id", "shared_by")
        v = Validator(Exists(*expected))
        if not v.validate(survey):
            logger.debug(v.errors)
            raise BadRequest(v.errors)
    respondent = get_respondent_by_party_id(pending_surveys[0]["shared_by"])
    try:
        get_respondent_by_email(pending_surveys[0]["email_address"])
        email_template = existing_user_email_template
    except NotFound:
        email_template = new_user_email_template
    if not respondent:
        raise BadRequest("Originator unknown")
    batch_number = uuid.uuid4()
    # logic to extract business list
    business_id_list = {pending_surveys["business_id"] for pending_surveys in pending_surveys}
    for business_id in business_id_list:
        business = get_business_by_id(business_id)
        business_list.append(business["name"])
    try:
        for pending_survey in pending_surveys:
            pending_survey_controller.pending_survey_create(
                business_id=pending_survey["business_id"],
                survey_id=pending_survey["survey_id"],
                email_address=pending_survey["email_address"],
                shared_by=pending_survey["shared_by"],
                batch_number=batch_number,
                is_transfer=is_transfer,
            )
    except SQLAlchemyError:
        raise BadRequest("This pending survey is already in progress")
    # logic to send email
    if is_transfer:
        verification_url = PublicWebsite().transfer_survey(batch_number)
    else:
        verification_url = PublicWebsite().share_survey(batch_number)
    personalisation = {
        "CONFIRM_EMAIL_URL": verification_url,
        "ORIGINATOR_EMAIL_ADDRESS": respondent.email_address,
        "BUSINESSES": business_list,
    }
    send_pending_survey_email(personalisation, email_template, pending_surveys[0]["email_address"], batch_number)
    return make_response(jsonify({"created": "success"}), 201)


def send_pending_survey_email(personalisation: dict, template: str, email: str, batch_id):
    """
    Send an email for share/transfer surveys
    :param personalisation dict of personalisation
    :param template str template name
    :param email str email id
    :param batch_id uuid batch_id
    """
    try:
        logger.info("sending email for share/transfer share", batch_id=str(batch_id))
        NotifyGateway(current_app.config).request_to_notify(
            email=email, template_name=template, personalisation=personalisation
        )
        logger.info("email for share/transfer survey sent", batch_id=str(batch_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error("Error sending email for share/transfer survey", batch_id=str(batch_id))


@pending_survey_view.route("/pending-survey/verification/<token>", methods=["GET"])
def share_survey_verification(token):
    """
    Verifies share/transfer survey verification email
    :param token
    :return json
    """
    response = pending_survey_controller.validate_pending_survey_token(token)
    return make_response(jsonify(response), 200)


@pending_survey_view.route("/pending-survey/confirm-pending-surveys/<batch_no>", methods=["POST"])
def confirm_pending_shares(batch_no):
    """
    Confirms pending survey
    :param batch_no
    """
    confirm_pending_survey(batch_no)
    return make_response(jsonify(), 201)


@pending_survey_view.route("/pending-surveys/<batch_no>", methods=["GET"])
def get_pending_surveys_with_batch_no(batch_no):
    """
    Get pending surveys by batch number
    :param batch_no
    """
    response = get_pending_survey_by_batch_number(batch_no)
    return make_response(jsonify(response), 200)


@pending_survey_view.route("/pending-surveys/originator/<originator_respondent_party_id>", methods=["GET"])
def get_pending_surveys_with_originator_respondent_party_id(originator_respondent_party_id):
    """
    Get pending surveys record against originator party id
    :param originator_respondent_party_id: Respondent party id
    :type originator_respondent_party_id: uuid
    """
    logger.info(
        "Retrieving share survey records against originator",
        originator_respondent_party_id=originator_respondent_party_id,
    )
    response = get_pending_survey_by_originator_respondent_id(originator_respondent_party_id)
    return make_response(jsonify(response), 200)


@pending_survey_view.route("/pending-surveys/<batch_no>", methods=["DELETE"])
def delete_pending_surveys_by_batch_number(batch_no):
    """
    Delete pending surveys record against a batch_number
    :param batch_no: batch number
    :type batch_no: uuid
    """
    logger.info("Attempting to delete pending surveys record against batch number", batch_no=batch_no)
    response = pending_survey_deletion(batch_no)
    return response


@pending_survey_view.route("/pending-surveys/resend-email", methods=["POST"])
def resend_pending_surveys_email():
    """
    Request to resend pending share email address against a single batch_number
    accepted payload:
    {
        'batch_number': #batch_number
    }
    """
    logger.info("Attempting to resend email for pending survey")
    payload = request.get_json() or {}
    if "batch_number" not in payload:
        logger.error("Invalid request")
        raise BadRequest("Invalid request - batch_number missing")
    batch_number = payload["batch_number"]
    logger.info("retrieving pending surveys against batch number", batch_number=batch_number)
    pending_surveys = get_pending_survey_by_batch_number(batch_number)
    logger.info("retrieving originator email address for resend email", batch_number=batch_number)
    originator = get_respondent_by_party_id(str(pending_surveys[0]["shared_by"]))
    respondent_email_address = pending_surveys[0]["email_address"]
    if "is_transfer" in pending_surveys[0]:
        verification_url = PublicWebsite().transfer_survey(batch_number)
        existing_user_email_template = "transfer_survey_access_existing_account"
        new_user_email_template = "transfer_survey_access_new_account"
    else:
        verification_url = PublicWebsite().share_survey(batch_number)
        existing_user_email_template = "share_survey_access_existing_account"
        new_user_email_template = "share_survey_access_new_account"
    try:
        # This is just to figure out if the respondent exist in our system, and hence it ignores the response.
        get_respondent_by_email(respondent_email_address)
        email_template = existing_user_email_template
    except NotFound:
        email_template = new_user_email_template
    business_list = []
    logger.info("retrieving list of business against batch number", batch_number=batch_number)
    business_id_list = {pending_survey["business_id"] for pending_survey in pending_surveys}
    for business_id in business_id_list:
        business = get_business_by_id(str(business_id))
        business_list.append(business["name"])
    personalisation = {
        "CONFIRM_EMAIL_URL": verification_url,
        "ORIGINATOR_EMAIL_ADDRESS": originator.email_address,
        "BUSINESSES": business_list,
    }
    logger.info("calling notify to resend email for pending share", batch_number=batch_number)
    send_pending_survey_email(personalisation, email_template, respondent_email_address, batch_number)
    logger.info("resend email for pending share send successfully", batch_number=batch_number)
    return make_response(jsonify({"resend_pending_surveys_email": "success"}), 201)
