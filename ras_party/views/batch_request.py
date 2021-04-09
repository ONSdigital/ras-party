import json
import logging
import structlog
from flask import Blueprint, current_app, make_response, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import abort
from ras_party.controllers import respondent_controller, share_survey_controller

logger = structlog.wrap_logger(logging.getLogger(__name__))
batch_request = Blueprint('batch_request', __name__)
auth = HTTPBasicAuth()


@batch_request.before_request
@auth.login_required
def before_respondent_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config['SECURITY_USER_NAME']
    config_password = current_app.config['SECURITY_USER_PASSWORD']
    if username == config_username:
        return config_password


@batch_request.route('/batch/respondents', methods=['DELETE'])
def delete_user_data_marked_for_deletion():
    """
    Endpoint Exposed for Kubernetes Cronjob to delete all respondents and
    its associated data marked for deletion
    """
    respondent_controller.delete_respondents_marked_for_deletion()
    return '', 204


@batch_request.route('/batch/requests', methods=['POST'])
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
    except ValueError as e:
        abort(400)

    responses = []

    for index, req in enumerate(requests):
        method = req['method']
        path = req['path']
        body = req.get('body', None)
        headers = req.get('headers', None)

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
        responses.append({
            "status": response.status_code,
        })

    return make_response(json.dumps(responses), 207)


@batch_request.route('/batch/pending-shares', methods=['DELETE'])
def delete_pending_surveys_deletion():
    """
    Endpoint Exposed for Kubernetes Cronjob to delete expired pending surveys
    """
    logger.info('Attempting to delete expired pending shares')
    share_survey_controller.delete_pending_shares()
    return '', 204
