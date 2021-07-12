from flask import Blueprint, jsonify, make_response

from ras_party.controllers import info_controller

info_view = Blueprint("info_view", __name__)


@info_view.route("/info", methods=["GET"])
def get_info():
    response = info_controller.get_info()
    return make_response(jsonify(response), 200)
