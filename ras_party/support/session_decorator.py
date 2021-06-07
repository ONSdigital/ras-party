import logging
from functools import wraps

import structlog
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.wrap_logger(logging.getLogger(__name__))


def handle_session(f, args, kwargs):
    session = current_app.db.session()
    try:
        with session.begin():
            result = f(*args, session=session, **kwargs)
            session.commit()
            return result
    except SQLAlchemyError as exc:
        logger.error(f"Rolling back database session due to {exc.__class__.__name__}", exc_info=True)
        session.rollback()
        raise SQLAlchemyError(f"{exc.__class__.__name__} occurred when committing to database", code=exc.code)
    except Exception:
        logger.error("Rolling back database session due to uncaught exception", exc_info=True)
        session.rollback()
        raise
    finally:
        current_app.db.session.remove()


def handle_query_only_session(f, args, kwargs):
    session = current_app.db.session()
    try:
        result = f(*args, session=session, **kwargs)
        return result
    except SQLAlchemyError:
        logger.error("Something went wrong accessing database", exc_info=True)
        raise
    finally:
        current_app.db.session.remove()


def handle_quiet_session(f, args, kwargs):
    session = current_app.db.session()
    try:
        result = f(*args, session=session, **kwargs)
        session.commit()
        return result
    except SQLAlchemyError:
        logger.error("Something went wrong accessing database", exc_info=True)
        session.rollback()
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


def with_quiet_db_session(f):
    """
    Wraps the supplied function, and introduces a correctly-scoped database session which is passed into the decorated
    function as the named parameter 'session'.  This is different from the @query_only_db_session in that it handles
    rollbacks for you on SQLAlchemyErrors as functions with this wrapper are ones that modify the database.
    Note:  This is meant to replace @with_db_session as a wrapper that doesn't log an error on every exception as
    every exception isn't worthy of a rollback and a logger.error line.  Once all  the @with_db_session's have been
    replaced with this, it'd be wise to change the name of this function to something more accurate.

    :param f: The function to be wrapped.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return handle_quiet_session(f, args, kwargs)

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
