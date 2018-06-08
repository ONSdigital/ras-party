import logging
from functools import wraps

import structlog
from flask import current_app

from ras_party.exceptions import RasError

logger = structlog.wrap_logger(logging.getLogger(__name__))


def handle_session(f, args, kwargs):
    logger.info("Acquiring database session.",
                pool_size=current_app.db.engine.pool.size(),
                connections_in_pool=current_app.db.engine.pool.checkedin(),
                connections_checked_out=current_app.db.engine.pool.checkedout(),
                current_overflow=current_app.db.engine.pool.overflow())
    session = current_app.db.session()
    try:
        result = f(*args, session=session, **kwargs)
        logger.info("Committing database session.")
        session.commit()
        return result
    except RasError:
        logger.error(f"Rolling back database session due to failure executing function")
        session.rollback()
        raise
    except Exception:
        logger.error("Rolling back database session due to uncaught exception")
        session.rollback()
        raise
    finally:
        logger.info("Removing database session.")
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
