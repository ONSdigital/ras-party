from flask import Blueprint

from ras_party.controllers import controller
from ras_party.controllers.log_decorator import log_route


info_view = Blueprint('info_view', __name__)


@info_view.route('/info', methods=['GET'])
@log_route
def get_info():
    return controller.get_info()
