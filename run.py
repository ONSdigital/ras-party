import logging
import os
from json import loads

import structlog
from flask import Flask
from flask_cors import CORS
from retrying import RetryError, retry
from sqlalchemy import column, create_engine, text
from sqlalchemy.exc import DatabaseError, ProgrammingError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists, select

from logger_config import logger_initial_config

logger = structlog.wrap_logger(logging.getLogger(__name__))


def create_app(config=None):
    # create and configure the Flask app.
    app = Flask(__name__)
    app.name = "ras-party"
    logger.info("Creating app", name=app.name)
    app_config = f"config.{config or os.environ.get('APP_SETTINGS', 'Config')}"
    app.config.from_object(app_config)

    # register view blueprints
    from ras_party import error_handlers
    from ras_party.views.account_view import account_view
    from ras_party.views.batch_request import batch_request
    from ras_party.views.business_view import business_view
    from ras_party.views.info_view import info_view
    from ras_party.views.party_view import party_view
    from ras_party.views.pending_survey_view import pending_survey_view
    from ras_party.views.respondent_view import respondent_view

    app.register_blueprint(party_view, url_prefix="/party-api/v1")
    app.register_blueprint(account_view, url_prefix="/party-api/v1")
    app.register_blueprint(business_view, url_prefix="/party-api/v1")
    app.register_blueprint(respondent_view, url_prefix="/party-api/v1")
    app.register_blueprint(batch_request, url_prefix="/party-api/v1")
    app.register_blueprint(pending_survey_view, url_prefix="/party-api/v1")
    app.register_blueprint(info_view)
    app.register_blueprint(error_handlers.blueprint)

    CORS(app)
    return app


def create_database(db_connection, db_schema):
    from ras_party.models import models

    engine = create_engine(db_connection, echo=True)
    session = scoped_session(sessionmaker())
    session.configure(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    engine.session = session
    models.Base.query = session.query_property()

    logger.info("Creating database")

    if db_connection.startswith("postgres"):
        # fix-up the postgres schema:
        for t in models.Base.metadata.sorted_tables:
            t.schema = db_schema

        q = exists(
            select([column("schema_name")])
            .select_from(text("information_schema.schemata"))
            .where(text(f"schema_name = '{db_schema}'"))
        )

        if not session().query(q).scalar():
            logger.info("Creating schema", schema=db_schema)
            engine.execute(f"CREATE SCHEMA {db_schema}")

            logger.info("Creating database tables")
            models.Base.metadata.create_all(engine)
        else:
            logger.info("Schema exists.", schema=db_schema)

    else:
        logger.info("Creating database tables.")
        models.Base.metadata.create_all(engine)

    logger.info("Ok, database tables have been created.")
    return engine


def retry_if_database_error(exception):
    logger.error("Database error has occurred", error=exception)
    return isinstance(exception, DatabaseError) and not isinstance(exception, ProgrammingError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def initialise_db(app):
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = create_database(app.config["DATABASE_URI"], app.config["DATABASE_SCHEMA"])


if __name__ == "__main__":
    app = create_app()
    with open(app.config["PARTY_SCHEMA"]) as io:
        app.config["PARTY_SCHEMA"] = loads(io.read())

    logger_initial_config(log_level=app.config["LOGGING_LEVEL"])

    try:
        initialise_db(app)
    except RetryError:
        logger.exception("Failed to initialise database")
        exit(1)

    scheme, host, port = app.config["SCHEME"], app.config["HOST"], int(app.config["PORT"])

    app.run(debug=app.config["DEBUG"], host=host, port=port)
