import structlog
from flask import jsonify
from flask_cors import CORS
from ras_common_utils.ras_config import ras_config
from ras_common_utils.ras_config.flask_extended import Flask
from ras_common_utils.ras_database.ras_database import RasDatabase
from ras_common_utils.ras_logger.ras_logger import configure_logger

from swagger_server.controllers.gw_registration import make_registration_func, call_in_background

"""
This is a duplicate of run.py, with minor modifications to support gunicorn execution.
"""

logger = structlog.get_logger()


def create_app(config):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_ras_config(config)

    @app.errorhandler(Exception)
    def handle_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # register view blueprints
    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')

    CORS(app)
    return app


def initialise_db(app):
    # Initialise the database with the specified SQLAlchemy model
    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', app.config)
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = db


config_path = 'config/config.yaml'
with open(config_path) as f:
    config = ras_config.from_yaml_file(config_path)

app = create_app(config)
configure_logger(app.config)
logger.debug("Created Flask app.")
logger.debug("Config is {}".format(app.config))

initialise_db(app)

scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])

if app.config.feature.gateway_registration:
    call_in_background(make_registration_func(app))
