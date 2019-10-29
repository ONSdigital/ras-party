import logging
from functools import wraps

import structlog
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.wrap_logger(logging.getLogger(__name__))


def handle_session(f, args, kwargs):
    logger.debug("Acquiring database session.",
                 pool_size=current_app.db.engine.pool.size(),
                 connections_in_pool=current_app.db.engine.pool.checkedin(),
                 connections_checked_out=current_app.db.engine.pool.checkedout(),
                 current_overflow=current_app.db.engine.pool.overflow())
    session = current_app.db.session()
    try:
        result = f(*args, session=session, **kwargs)
        logger.debug("Committing database session.")
        session.commit()
        return result
    except SQLAlchemyError as exc:
        logger.exception(f"Rolling back database session due to {exc.__class__.__name__}",
                         pool_size=current_app.db.engine.pool.size(),
                         connections_in_pool=current_app.db.engine.pool.checkedin(),
                         connections_checked_out=current_app.db.engine.pool.checkedout(),
                         current_overflow=current_app.db.engine.pool.overflow())
        session.rollback()
        raise SQLAlchemyError(f"{exc.__class__.__name__} occurred when committing to database", code=exc.code)
    except Exception:
        logger.exception("Rolling back database session due to uncaught exception",
                         pool_size=current_app.db.engine.pool.size(),
                         connections_in_pool=current_app.db.engine.pool.checkedin(),
                         connections_checked_out=current_app.db.engine.pool.checkedout(),
                         current_overflow=current_app.db.engine.pool.overflow())
        session.rollback()
        raise
    finally:
        logger.debug("Removing database session.")
        current_app.db.session.remove()


def handle_query_only_session(f, args, kwargs):
    session = current_app.db.session()
    try:
        result = f(*args, session=session, **kwargs)
        return result
    except SQLAlchemyError:
        logger.exception("Something went wrong accessing database",
                         pool_size=current_app.db.engine.pool.size(),
                         connections_in_pool=current_app.db.engine.pool.checkedin(),
                         connections_checked_out=current_app.db.engine.pool.checkedout(),
                         current_overflow=current_app.db.engine.pool.overflow())
        raise
    finally:
        current_app.db.session.remove()


def with_db_session(f):
    """
    Wraps the supplied function, and introduces a correctly-scoped database session which is passed into the decorated
    function as the named parameter 'session'.

    :param f: The function to be wrapped.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return handle_session(f, args, kwargs)

    return wrapper


def with_query_only_db_session(f):
    """
    Wraps the supplied function, and introduces a correctly-scoped database session which is passed into the decorated
    function as the named parameter 'session'. This differs from @with_db_session as this one doesn't handle commits
    and rollbacks as the function is only meant to be getting information without changing anything.

    It also only handles SQLAlchemyError as the calling function is expected to handle its own non-db related errors.

    This should be removed once a better solution is found.  This function is only being added as a short term fix to
    reduce the number of logger.exception lines that aren't actually problems happening in the system.

    :param f: The function to be wrapped.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return handle_query_only_session(f, args, kwargs)

    return wrapper
