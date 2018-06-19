import os
import logging
from json import loads

import asyncio
import structlog
from alembic.config import Config as AlembicConfig
from alembic import command
from aiohttp import web
from flask_cors import CORS
from retrying import retry, RetryError
from sqlalchemy import create_engine, column, text
from sqlalchemy.exc import DatabaseError, ProgrammingError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists, select

from config import Config, DevelopmentConfig, TestingConfig
from logger_config import logger_initial_config
from ras_party.consumer import MessageConsumer
from sdc.rabbit.publishers import QueuePublisher
from ras_party.db_handler import db_handler
from ras_party.error_handlers import error_handler
from ras_party.views.business_view import post_business, get_business_by_id, put_business_attributes_ce


logger = structlog.wrap_logger(logging.getLogger(__name__))


def create_app(config=None):
    # create and configure the Flask app
    config = config or os.environ.get('APP_SETTINGS', 'Config')
    config_obj = {
        "Config": Config,
        "DevelopmentConfig": DevelopmentConfig,
        "TestingConfig": TestingConfig
    }[config]()

    app = web.Application(middlewares=[error_handler, db_handler], debug=config_obj.DEBUG)

    app.config = config_obj

    app.router.add_post('/party-api/v1/businesses', post_business)
    app.router.add_get('/party-api/v1/businesses/id/{business_id}', get_business_by_id)
    app.router.add_put('/party-api/v1/businesses/sample/link/{sample}', put_business_attributes_ce)

    # register view blueprints
    # from ras_party.views.party_view import party_view
    # from ras_party.views.respondent_view import respondent_view
    # from ras_party.views.account_view import account_view
    # from ras_party.views.info_view import info_view
    # app.register_blueprint(party_view, url_prefix='/party-api/v1')
    # app.register_blueprint(account_view, url_prefix='/party-api/v1')
    # app.register_blueprint(respondent_view, url_prefix='/party-api/v1')
    # app.register_blueprint(info_view)

    # CORS(app)
    return app


def create_database(db_connection, db_schema, pool_size, max_overflow, pool_recycle):
    from ras_party.models import models

    engine = create_engine(db_connection, convert_unicode=True, pool_size=pool_size, max_overflow=max_overflow,
                           pool_recycle=pool_recycle)
    session = scoped_session(sessionmaker())
    session.configure(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    # TODO: change this
    engine.session = session

    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.attributes['configure_logger'] = False

    logger.info("Creating database")

    if db_connection.startswith('postgres'):
        # fix-up the postgres schema:
        for t in models.Base.metadata.sorted_tables:
            t.schema = db_schema

        q = exists(select([column('schema_name')]).select_from(text("information_schema.schemata"))
                   .where(text(f"schema_name = '{db_schema}'")))

        if not session().query(q).scalar():
            logger.info("Creating schema", schema=db_schema)
            engine.execute(f"CREATE SCHEMA {db_schema}")

            logger.info("Creating database tables.")
            models.Base.metadata.create_all(engine)

            logger.info("Alembic table stamped")
            command.stamp(alembic_cfg, "head")
        else:
            logger.info("Schema exists.", schema=db_schema)

            logger.info("Running Alembic database upgrade")
            command.upgrade(alembic_cfg, "head")
    else:
        logger.info("Creating database tables.")
        models.Base.metadata.create_all(engine)

    logger.info("Ok, database tables have been created.")
    return engine


def retry_if_database_error(exception):
    logger.error('Database error has occurred', error=exception)
    return isinstance(exception, DatabaseError) and not isinstance(exception, ProgrammingError)


def initialise_db(app):
    app.db = create_database(app.config.DATABASE_URI, app.config.DATABASE_SCHEMA, app.config.DB_POOL_SIZE,
                             app.config.DB_MAX_OVERFLOW, app.config.DB_POOL_RECYCLE)


def process(message, tx_id):
    logger.info("Message consumed", tx_id=tx_id, message=message)


def listen_to_rabbit(app):
    logger.info("Setting up queue")
    publisher = QueuePublisher(urls=app.config.RABBIT_URLS,
                               queue=app.config.RABBIT_QUARANTINE_QUEUE)
    consumer = MessageConsumer(durable_queue=True, exchange=app.config.RABBIT_EXCHANGE, exchange_type="topic",
                               rabbit_queue=app.config.RABBIT_QUEUE,
                               rabbit_urls=app.config.RABBIT_URLS, quarantine_publisher=publisher,
                               process=process)
    try:
        consumer.run()
    except asyncio.CancelledError:
        pass
    finally:
        consumer.stop()

async def start_background_tasks(app):
    app['rabbit_listener'] = app.loop.create_task(listen_to_rabbit(app))

async def cleanup_background_tasks(app):
    app['rabbit_listener'].cancel()
    await app['rabbit_listener']

# def dispose_db(app):
#     app['db'].dispose()

if __name__ == '__main__':
    app = create_app()
    # with open(app.config.PARTY_SCHEMA) as io:
    #     app.config.PARTY_SCHEMA = loads(io.read())

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    logger_initial_config(service_name='ras-party', log_level=app.config.LOGGING_LEVEL)

    initialise_db(app)
    # app.on_cleanup.append(dispose_db)

    scheme, host, port = app.config.SCHEME, app.config.HOST, int(app.config.PORT)

    web.run_app(app, host=host, port=port)
