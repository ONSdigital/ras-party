import logging
from functools import wraps

import structlog

logger = structlog.wrap_logger(logging.getLogger(__name__))


class Transaction:

    """
    Provides a simple wrapper around a list of compensating actions, where each action is a function
    taking no parameters. rollback will apply each function in the order it was added to the 'transaction'.
    """

    def __init__(self):
        self._compensating_actions = []
        self._success_actions = []

    def compensate(self, c):
        self._compensating_actions.append(c)

    def on_success(self, f):
        self._success_actions.append(f)

    def commit(self):
        for func in self._success_actions:
            func()

    def rollback(self):
        if self._compensating_actions:
            logger.info("Attempting to rollback any modifications.")
        else:
            logger.info("No rollback actions are required.")
        for i, action in enumerate(self._compensating_actions):
            logger.info("Applying compensating action", number=i + 1)
            self._apply(action)

    def _apply(self, f):
        try:
            f()
        except Exception:
            logger.exception(
                "Fatal: error while attempting to compensate a distributed transaction."
            )
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
            kwargs["tran"] = tran
            result = f(*args, **kwargs)
            tran.commit()
            return result
        except Exception:
            tran.rollback()
            raise

    return wrapper
