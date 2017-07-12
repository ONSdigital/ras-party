import os

import structlog
from flask_cors import CORS
from ons_ras_common.ras_config import ras_config
from ons_ras_common.ras_database.ras_database import RasDatabase
from ons_ras_common.ras_logger.ras_logger import configure_logger

from ons_ras_common.ras_config.flask_extended import Flask


logger = structlog.get_logger()


def create_app(config):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_ras_config(config)

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


if __name__ == '__main__':
    config_path = 'config/config.yaml'
    with open(config_path) as f:
        config = ras_config.from_yaml_file(config_path)

    app = create_app(config)
    configure_logger(app.config)
    logger.debug("Created Flask app.")
    logger.debug("Config is {}".format(app.config))

    initialise_db(app)

    # TODO: reintroduce gw registration, which is just a case of iterating endpoints and posting to gw
    # If 5-sec iterative reg is required, then use asyncio

    scheme, host, port = app.config['scheme'], app.config['host'], app.config['port']
    # for rule in app.url_map.iter_rules():
    #     # TODO: how does the gw recognise parameterised endpoints? (perhaps just first part of endpoint?)
    #     reg = {'protocol': scheme, 'host': host, 'port': port, 'uri': rule.rule}
    #     print(reg)
    print ("***** app.config.debug is: {} ******\n".format(app.config['debug']))
    #app.run(debug=app.config['debug'], port=port)
    app.run(debug=True, port=port)
