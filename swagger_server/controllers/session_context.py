from contextlib import contextmanager

from flask import current_app


@contextmanager
def transaction():
    Session = current_app.db.session
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        Session.remove()
