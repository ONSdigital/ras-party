from functools import wraps

import structlog

log = structlog.get_logger()


class Transaction:

    """
    Provides a simple wrapper around a list of compensating actions, where each action is a function
    taking no parameters. rollback will apply each function in the order it was added to the 'transaction'.
    """

    def __init__(self):
        self._compensating_actions = []

    def compensate(self, c):
        self._compensating_actions.append(c)

    def rollback(self):
        if self._compensating_actions:
            log.info("Attempting to rollback any modifications.")
        else:
            log.info("No rollback actions are required.")
        for i, action in enumerate(self._compensating_actions):
            log.info("Applying compensating action #{}".format(i+1))
            self._apply(action)

    def _apply(self, f):
        try:
            f()
        except Exception as e:
            log.error("Fatal: error while attempting to compensate a distributed transaction.")
            log.error("Details: {}".format(e))
            raise


def transactional(f):
    """
    Convenience decorator to inject a Transaction instance into the wrapped function.
    Exception from the wrapped function causes the rollback action(s) to be applied.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        tran = Transaction()
        try:
            kwargs['tran'] = tran
            return f(*args, **kwargs)
        except Exception:
            tran.rollback()
            raise

    return wrapper
