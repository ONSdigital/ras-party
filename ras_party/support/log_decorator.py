import logging
from functools import wraps

import structlog


logger = structlog.wrap_logger(logging.getLogger(__name__))


def log_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.info("Calling route handler", function=f.__name__, args=args, kwargs=kwargs)
        result = f(*args, **kwargs)
        logger.info("Returning from route handler function", function=f.__name__)
        return result

    return wrapper
