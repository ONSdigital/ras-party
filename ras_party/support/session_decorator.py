from functools import wraps
import logging

from flask import current_app
import structlog

from ras_party.exceptions import RasError, RasDatabaseError


logger = structlog.wrap_logger(logging.getLogger(__name__))


def with_db_session(f):
    """
    Wraps the supplied function, and introduces a correctly-scoped database session which is passed into the decorated
    function as the named parameter 'session'.

    :param f: The function to be wrapped.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.info("Acquiring database session.")
        session = current_app.db.session()
        try:
            result = f(*args, session=session, **kwargs)
            logger.info("Committing database session.")
            session.commit()
            return result
        except RasError:
            logger.info("Rolling-back database session.")
            session.rollback()
            raise
        except Exception as e:
            logger.info("Rolling-back database session.")
            logger.exception("There was an error committing the changes to the database.")
            session.rollback()
            raise RasDatabaseError("There was an error committing the changes to the database.", error=e)
        finally:
            logger.info("Removing database session.")
            current_app.db.session.remove()
    return wrapper
