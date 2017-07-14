from contextlib import contextmanager

from flask import current_app

from swagger_server.controllers.ras_error import RasDatabaseError


@contextmanager
def transaction():
    Session = current_app.db.session
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise RasDatabaseError("There was an error committing the changes to the database. Details: {}".format(e))
    finally:
        Session.remove()
