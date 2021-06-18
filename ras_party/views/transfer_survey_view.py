import logging
import uuid

import structlog
from flask import Blueprint, request, make_response, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers import pending_survey_controller
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.respondent_controller import get_respondent_by_id, get_respondent_by_email
from ras_party.controllers.pending_survey_controller import get_pending_survey_by_batch_number, confirm_share_survey
from ras_party.controllers.validate import Validator, Exists
from ras_party.exceptions import RasNotifyError
from ras_party.support.public_website import PublicWebsite
from ras_party.views.account_view import auth

transfer_survey_view = Blueprint('transfer_survey_view', __name__)
logger = structlog.wrap_logger(logging.getLogger(__name__))


@transfer_survey_view.before_request
@auth.login_required
def before_transfer_survey_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@transfer_survey_view.route('/transfer-survey-users-count', methods=['GET'])
def transfer_survey_users():
    """
    Get total users count who are already enrolled and pending transfer survey against business id and survey id
    """
    business_id = request.args.get('business_id')
    survey_id = request.args.get('survey_id')
    if business_id and survey_id:
        # this is just to validate that the business_id exists
        get_business_by_id(business_id)
        response = pending_survey_controller.get_users_enrolled_and_pending_survey_against_business_and_survey(
            business_id, survey_id, True)
        return make_response(jsonify(response), 200)
    else:
        raise BadRequest('Business id and Survey id is required for this request.')


@transfer_survey_view.route('/transfer-surveys', methods=['POST'])
def post_pending_transfer_surveys():
    """
     Creates new records for pending shares
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
    try:
        pending_transfers = payload['pending_transfers']
        business_list = []
        if len(pending_transfers) == 0:
            raise BadRequest('Payload Invalid - pending_transfers list is empty')
        for surveys in pending_transfers:
            # Validation, curation and checks
            expected = ('email_address', 'survey_id', 'business_id', 'shared_by')
            v = Validator(Exists(*expected))
            if not v.validate(surveys):
                logger.debug(v.errors)
                raise BadRequest(v.errors)
        respondent = get_respondent_by_id(pending_transfers[0]['shared_by'])
        try:
            get_respondent_by_email(pending_transfers[0]['email_address'])
            email_template = 'transfer_survey_access_existing_account'
        except NotFound:
            email_template = 'transfer_survey_access_new_account'
        if not respondent:
            raise BadRequest('Originator unknown')
        batch_number = uuid.uuid4()
        for pending_transfer in pending_transfers:
            business = get_business_by_id(pending_transfer['business_id'])
            business_list.append(business['name'])
            pending_survey_controller.pending_transfer_survey_create(business_id=pending_transfer['business_id'],
                                                                     survey_id=pending_transfer['survey_id'],
                                                                     email_address=pending_transfer['email_address'],
                                                                     shared_by=pending_transfer['shared_by'],
                                                                     batch_number=batch_number)
        # logic to send email
        verification_url = PublicWebsite().transfer_survey(batch_number)
        personalisation = {'CONFIRM_EMAIL_URL': verification_url,
                           'ORIGINATOR_EMAIL_ADDRESS': respondent['emailAddress'],
                           'BUSINESSES': business_list}
        send_pending_transfer_email(personalisation, email_template, pending_transfers[0]['email_address'],
                                    batch_number)
        return make_response(jsonify({"created": "success"}), 201)
    except KeyError:
        raise BadRequest('Payload Invalid - Pending transfer key missing')

    except SQLAlchemyError:
        raise BadRequest('This transfer is already in progress')


def send_pending_transfer_email(personalisation: dict, template: str, email: str, batch_id):
    """
    Send an email for transfer surveys
    :param personalisation dict of personalisation
    :param template str template name
    :param email str email id
    :param batch_id uuid batch_id
    """
    try:
        logger.info('sending email for transfer share', batch_id=str(batch_id))
        NotifyGateway(current_app.config).request_to_notify(email=email,
                                                            template_name=template,
                                                            personalisation=personalisation)
        logger.info('email for survey transfer sent', batch_id=str(batch_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending email for survey transfer', batch_id=str(batch_id))


@transfer_survey_view.route('/transfer-survey/verification/<token>', methods=['GET'])
def share_survey_verification(token):
    """
    Verifies transfer survey verification email
    :param token
    :return json
    """
    response = pending_survey_controller.validate_pending_survey_token(token)
    return make_response(jsonify(response), 200)


@transfer_survey_view.route('/transfer-survey/confirm-pending-transfers/<batch_no>', methods=['POST'])
def confirm_pending_transfers(batch_no):
    """
    Confirms pending transfer survey
    :param batch_no
    """
    confirm_share_survey(batch_no)
    return make_response(jsonify(), 201)


@transfer_survey_view.route('/transfer-survey/<batch_no>', methods=['GET'])
def get_pending_transfer_with_batch_no(batch_no):
    """
    Confirms pending transfer survey
    :param batch_no
    """
    response = get_pending_survey_by_batch_number(batch_no)
    return make_response(jsonify(response), 200)
