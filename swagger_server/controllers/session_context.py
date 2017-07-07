from contextlib import contextmanager

from microservice import db

Session = db.session


@contextmanager
def transaction():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        Session.remove()
