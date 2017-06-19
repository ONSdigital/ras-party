from contextlib import contextmanager

from ons_ras_common import ons_env

Session = ons_env.db.session


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


