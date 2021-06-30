import logging
import uuid

import structlog
from flask import Blueprint, request, make_response, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers import pending_survey_controller
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.pending_survey_controller import get_pending_survey_by_batch_number, \
    confirm_pending_survey
from ras_party.controllers.respondent_controller import get_respondent_by_id, get_respondent_by_email
from ras_party.controllers.validate import Validator, Exists
from ras_party.exceptions import RasNotifyError
from ras_party.support.public_website import PublicWebsite
from ras_party.views.account_view import auth

pending_survey_view = Blueprint('pending_survey_view', __name__)
logger = structlog.wrap_logger(logging.getLogger(__name__))


@pending_survey_view.before_request
@auth.login_required
def before_pending_survey_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@pending_survey_view.route('/pending-survey-users-count', methods=['GET'])
def pending_survey_users():
    """
    Get total users count who are already enrolled and pending transfer survey against business id and survey id
    """
    business_id = request.args.get('business_id')
    survey_id = request.args.get('survey_id')
    is_transfer = request.args.get('is_transfer', False)
    if business_id and survey_id:
        # this is just to validate that the business_id exists
        get_business_by_id(business_id)
        response = pending_survey_controller.get_users_enrolled_and_pending_survey_against_business_and_survey(
            business_id, survey_id, is_transfer)
        return make_response(jsonify(response), 200)
    else:
        raise BadRequest('Business id and Survey id is required for this request.')


@pending_survey_view.route('/pending-surveys', methods=['POST'])
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
    if 'pending_shares' not in payload and 'pending_transfers' not in payload:
        raise BadRequest('Payload Invalid - Pending survey key missing')
    if 'pending_shares' in payload:
        is_transfer = False
        pending_surveys = payload['pending_shares']
        existing_user_email_template = 'share_survey_access_existing_account'
        new_user_email_template = 'share_survey_access_new_account'
    else:
        is_transfer = True
        pending_surveys = payload['pending_transfers']
        existing_user_email_template = 'transfer_survey_access_existing_account'
        new_user_email_template = 'transfer_survey_access_new_account'

    business_list = []
    if len(pending_surveys) == 0:
        raise BadRequest('Payload Invalid - pending_surveys list is empty')
    for survey in pending_surveys:
        # Validation, curation and checks
        expected = ('email_address', 'survey_id', 'business_id', 'shared_by')
        v = Validator(Exists(*expected))
        if not v.validate(survey):
            logger.debug(v.errors)
            raise BadRequest(v.errors)
    respondent = get_respondent_by_id(pending_surveys[0]['shared_by'])
    try:
        get_respondent_by_email(pending_surveys[0]['email_address'])
        email_template = existing_user_email_template
    except NotFound:
        email_template = new_user_email_template
    if not respondent:
        raise BadRequest('Originator unknown')
    batch_number = uuid.uuid4()
    try:
        for pending_survey in pending_surveys:
            business = get_business_by_id(pending_survey['business_id'])
            business_list.append(business['name'])
            pending_survey_controller.pending_survey_create(business_id=pending_survey['business_id'],
                                                            survey_id=pending_survey['survey_id'],
                                                            email_address=pending_survey['email_address'],
                                                            shared_by=pending_survey['shared_by'],
                                                            batch_number=batch_number,
                                                            is_transfer=is_transfer)
    except SQLAlchemyError:
        raise BadRequest('This pending survey is already in progress')
    # logic to send email
    if is_transfer:
        verification_url = PublicWebsite().transfer_survey(batch_number)
    else:
        verification_url = PublicWebsite().share_survey(batch_number)
    personalisation = {'CONFIRM_EMAIL_URL': verification_url,
                       'ORIGINATOR_EMAIL_ADDRESS': respondent['emailAddress'],
                       'BUSINESSES': business_list}
    send_pending_survey_email(personalisation, email_template, pending_surveys[0]['email_address'], batch_number)
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
        logger.info('sending email for share/transfer share', batch_id=str(batch_id))
        NotifyGateway(current_app.config).request_to_notify(email=email,
                                                            template_name=template,
                                                            personalisation=personalisation)
        logger.info('email for share/transfer survey sent', batch_id=str(batch_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending email for share/transfer survey', batch_id=str(batch_id))


@pending_survey_view.route('/pending-survey/verification/<token>', methods=['GET'])
def share_survey_verification(token):
    """
    Verifies share/transfer survey verification email
    :param token
    :return json
    """
    response = pending_survey_controller.validate_pending_survey_token(token)
    return make_response(jsonify(response), 200)


@pending_survey_view.route('/pending-survey/confirm-pending-surveys/<batch_no>', methods=['POST'])
def confirm_pending_shares(batch_no):
    """
    Confirms pending share survey
    :param batch_no
    """
    pending_surveys_list = confirm_pending_survey(batch_no)
    batch_no = str(pending_surveys_list[0]['batch_no'])
    pending_surveys_is_transfer = pending_surveys_list[0].get('is_transfer', False)
    try:
        respondent = get_respondent_by_id(str(pending_surveys_list[0]['shared_by']))
        if pending_surveys_is_transfer:
            confirmation_email_template = 'transfer_survey_access_confirmation'
        else:
            confirmation_email_template = 'share_survey_access_confirmation'
        business_list = []
        for survey in pending_surveys_list:
            business = get_business_by_id(str(survey['business_id']))
            business_list.append(business['name'])
        personalisation = {'NAME': respondent['firstName'],
                           'COLLEAGUE_EMAIL_ADDRESS': pending_surveys_list[0]['email_address'],
                           'BUSINESSES': business_list}
        send_pending_survey_email(personalisation, confirmation_email_template, respondent['emailAddress'],
                                  batch_no)
    # Exception is used to abide by the notify controller. At this point of time the pending share has been accepted
    # hence if the email phase fails it should not disrupt the flow.
    except Exception as e:  # noqa
        logger.error('Error sending confirmation email for pending share', batch_no=batch_no,
                     email=pending_surveys_list[0]['shared_by'])
    return make_response(jsonify(), 201)


@pending_survey_view.route('/pending-surveys/<batch_no>', methods=['GET'])
def get_pending_surveys_with_batch_no(batch_no):
    """
    Confirms pending share survey
    :param batch_no
    """
    response = get_pending_survey_by_batch_number(batch_no)
    return make_response(jsonify(response), 200)
