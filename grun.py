import os

import structlog
from flask_cors import CORS
from ons_ras_common.ras_database.ras_database import RasDatabase
from ons_ras_common.ras_logger.ras_logger import configure_logger

from ons_ras_common.ras_config.flask_extended import Flask


logger = structlog.get_logger()


def create_app(config_file):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_yaml(os.path.join(app.root_path, config_file))
    configure_logger(app.config)

    # Initialise the database with the specified SQLAlchemy model
    PartyDatabase = RasDatabase.make(model_paths=['swagger_server.models.models'])
    db = PartyDatabase('ras-party-db', app.config)
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = db

    # register view blueprints
    from ras_party.views.party_view import party_view
    app.register_blueprint(party_view, url_prefix='/party-api/v1')

    CORS(app)
    return app


app = create_app('config/local.yaml')
