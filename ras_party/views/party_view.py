from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_httpauth import HTTPBasicAuth
import logging
import structlog
from ras_party.controllers import party_controller

party_view = Blueprint("party_view", __name__)
auth = HTTPBasicAuth()

logger = structlog.wrap_logger(logging.getLogger(__name__))


@party_view.before_request
@auth.login_required
def before_party_view():
    pass


@auth.get_password
def get_pw(username):
    config_username = current_app.config["SECURITY_USER_NAME"]
    config_password = current_app.config["SECURITY_USER_PASSWORD"]
    if username == config_username:
        return config_password


@party_view.route("/parties", methods=["POST"])
def post_party():
    logger.info("Started processing CSV queries at " + str(datetime.now()))
    payload = request.get_json() or {}
    response = party_controller.parties_post(payload)
    logger.info("Finished processing CSV queries at " + str(datetime.now()))
    return jsonify(response)


@party_view.route("/parties", methods=["PATCH"])
def patch_party():
    payload = request.get_json() or {}
    response = party_controller.parties_patch(payload)
    return jsonify(response)


@party_view.route("/parties/type/<sample_unit_type>/id/<id>", methods=["GET"])
def get_party_by_id(sample_unit_type, id):
    survey_id = request.args.get("survey_id")
    enrolment_status = request.args.getlist("enrolment_status")

    if survey_id:
        response = party_controller.get_party_with_enrolments_filtered_by_survey(
            sample_unit_type, id, survey_id, enrolment_status
        )
    else:
        response = party_controller.get_party_by_id(sample_unit_type, id)

    return jsonify(response)
