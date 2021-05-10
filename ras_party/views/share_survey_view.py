import logging
import uuid

import structlog
from flask import Blueprint, request, make_response, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from ras_party.controllers import share_survey_controller
from ras_party.controllers.business_controller import get_business_by_id
from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.controllers.respondent_controller import get_respondent_by_id, get_respondent_by_email
from ras_party.controllers.validate import Validator, Exists
from ras_party.exceptions import RasNotifyError
from ras_party.support.public_website import PublicWebsite
from ras_party.views.account_view import auth

share_survey_view = Blueprint('share_survey_view', __name__)
logger = structlog.wrap_logger(logging.getLogger(__name__))


@share_survey_view.before_request
@auth.login_required
def before_share_survey_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@share_survey_view.route('/share-survey-users-count', methods=['GET'])
def share_survey_users():
    """
    Get total users count who are already enrolled and pending share survey against business id and survey id
    """
    business_id = request.args.get('business_id')
    survey_id = request.args.get('survey_id')
    if business_id and survey_id:
        # this is just to validate that the business_id exists
        get_business_by_id(business_id)
        response = share_survey_controller.get_users_enrolled_and_pending_share_against_business_and_survey(business_id,
                                                                                                            survey_id)
        return make_response(jsonify(response), 200)
    else:
        raise BadRequest('Business id and Survey id is required for this request.')


@share_survey_view.route('/pending-shares', methods=['POST'])
def post_pending_shares():
    """
     Creates new records for pending shares
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
    """
    payload = request.get_json() or {}
    try:
        pending_shares = payload['pending_shares']
        business_list = []
        if len(pending_shares) == 0:
            raise BadRequest('Payload Invalid - pending_shares list is empty')
        for share in pending_shares:
            # Validation, curation and checks
            expected = ('email_address', 'survey_id', 'business_id', 'shared_by')
            v = Validator(Exists(*expected))
            if not v.validate(share):
                logger.debug(v.errors)
                raise BadRequest(v.errors)
        respondent = get_respondent_by_id(pending_shares[0]['shared_by'])
        try:
            existing_account = get_respondent_by_email(pending_shares[0]['email_address'])
            email_template = 'share_survey_access_existing_account'
        except NotFound:
            email_template = 'share_survey_access_new_account'
        if not respondent:
            raise BadRequest('Originator unknown')
        batch_number = uuid.uuid4()
        for pending_share in pending_shares:
            business = get_business_by_id(pending_share['business_id'])
            business_list.append(business['name'])
            share_survey_controller.pending_share_create(business_id=pending_share['business_id'],
                                                         survey_id=pending_share['survey_id'],
                                                         email_address=pending_share['email_address'],
                                                         shared_by=pending_share['shared_by'],
                                                         batch_number=batch_number)
        # Add logic to send email
        verification_url = PublicWebsite().share_survey(batch_number)
        personalisation = {'CONFIRM_EMAIL_URL': verification_url,
                           'ORIGINATOR_EMAIL_ADDRESS': respondent['emailAddress'],
                           'BUSINESSES': business_list}
        _send_pending_share_email(personalisation, email_template, pending_shares[0]['email_address'], batch_number)
        return make_response(jsonify({"created": "success"}), 201)
    except KeyError:
        raise BadRequest('Payload Invalid - Pending share key missing')

    except SQLAlchemyError:
        raise BadRequest('This share is already in progress')


def _send_pending_share_email(personalisation, template, email, batch_id):
    """
    Send an email for sharing surveys
    """
    try:
        logger.info('sending email for survey share', batch_id=str(batch_id))
        NotifyGateway(current_app.config).request_to_notify(email=email,
                                                            template_name=template,
                                                            personalisation=personalisation)
        logger.info('email for survey share sent', batch_id=str(batch_id))
    except RasNotifyError:
        # Note: intentionally suppresses exception
        logger.error('Error sending sending email for survey share', batch_id=str(batch_id))
