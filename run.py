from json import loads

import structlog
from flask_cors import CORS
from ras_common_utils.ras_config import ras_config
from ras_common_utils.ras_config.flask_extended import Flask
from ras_common_utils.ras_database.ras_database import RasDatabase
from ras_common_utils.ras_logger.ras_logger import configure_logger
from retrying import retry, RetryError
from sqlalchemy.exc import DatabaseError

logger = structlog.get_logger()


def create_app(config):
    # create and configure the Flask app
    app = Flask(__name__)
    app.config.from_ras_config(config)

    # register view blueprints
    from ras_party.views.party_view import party_view
    from ras_party.views.business_view import business_view
    from ras_party.views.respondent_view import respondent_view
    from ras_party.views.account_view import account_view
    from ras_party.views.info_view import info_view
    from ras_party import error_handlers
    app.register_blueprint(party_view, url_prefix='/party-api/v1')
    app.register_blueprint(account_view, url_prefix='/party-api/v1')
    app.register_blueprint(business_view, url_prefix='/party-api/v1')
    app.register_blueprint(respondent_view, url_prefix='/party-api/v1')
    app.register_blueprint(info_view)
    app.register_blueprint(error_handlers.blueprint)

    CORS(app)
    return app


def retry_if_database_error(exception):
    return isinstance(exception, DatabaseError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def initialise_db(app):
    # Initialise the database with the specified SQLAlchemy model
    party_database = RasDatabase.make(model_paths=['ras_party.models.models'])
    db = party_database('ras-party-db', app.config)
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = db


if __name__ == '__main__':
    config_path = 'config/config.yaml'

    config = ras_config.from_yaml_file(config_path)
    configure_logger(config.service)

    app = create_app(config)
    with open(app.config['PARTY_SCHEMA']) as io:
        app.config['PARTY_SCHEMA'] = loads(io.read())

    try:
        initialise_db(app)
    except RetryError:
        logger.exception('Failed to initialise database')
        exit(1)

    scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])

    app.run(debug=app.config['DEBUG'], host=host, port=port)
