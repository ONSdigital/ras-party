from contextlib import contextmanager

from microservice import PartyService

service = PartyService().get()


@contextmanager
def transaction():
    session = service.db.session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        service.db.session.remove()
