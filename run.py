import logging
from json import loads

import structlog
from flask import _app_ctx_stack
from flask_cors import CORS
from ras_common_utils.ras_config.flask_extended import Flask
from ras_common_utils.ras_config import ras_config
from retrying import retry, RetryError
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import scoped_session, sessionmaker

from logger_config import logger_initial_config


logger = structlog.wrap_logger(logging.getLogger(__name__))


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


def create_database(db_connection, db_schema):
    from ras_party.models import models

    engine = create_engine(db_connection, convert_unicode=True)
    session = scoped_session(sessionmaker(), scopefunc=lambda: _app_ctx_stack.__ident_func__())
    session.configure(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    # TODO: change this
    engine.session = session

    # fix-up the postgres schema:
    if db_connection.startswith('postgres'):
        for t in models.Base.metadata.sorted_tables:
            t.schema = db_schema

    logger.info("Creating database with uri '{db_connection}'")
    if db_connection.startswith('postgres'):
        logger.info("Creating schema {db_schema}.")
        engine.execute("CREATE SCHEMA IF NOT EXISTS {db_schema}")
    logger.info("Creating database tables.")
    models.Base.metadata.create_all(engine)
    logger.info("Ok, database tables have been created.")
    return engine


def retry_if_database_error(exception):
    return isinstance(exception, DatabaseError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def initialise_db(app):
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = create_database(app.config['DATABASE_URI'], app.config['DATABASE_SCHEMA'])


if __name__ == '__main__':
    config_path = 'config/config.yaml'

    config = ras_config.from_yaml_file(config_path)

    app = create_app(config)
    with open(app.config['PARTY_SCHEMA']) as io:
        app.config['PARTY_SCHEMA'] = loads(io.read())

    logger_initial_config(service_name='ras-party', log_level=app.config['LOG_LEVEL'])

    try:
        initialise_db(app)
    except RetryError:
        logger.exception('Failed to initialise database')
        exit(1)

    scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])

    app.run(debug=app.config['DEBUG'], host=host, port=port)
