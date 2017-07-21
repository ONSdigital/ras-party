from contextlib import contextmanager

from flask import current_app
from structlog import get_logger

from ras_party.controllers.ras_error import RasDatabaseError, RasError

log = get_logger()


@contextmanager
def db_session():
    Session = current_app.db.session
    session = Session()
    try:
        yield session
        session.commit()
    except RasError:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise RasDatabaseError("There was an error committing the changes to the database. Details: {}".format(e))
    finally:
        Session.remove()
