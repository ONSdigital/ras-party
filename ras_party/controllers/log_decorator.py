from functools import wraps

import structlog

logger = structlog.get_logger()


def log_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.info("Calling route handler function '{}' with args={}, kwargs={}".format(f.__name__, args, kwargs))
        result = f(*args, **kwargs)
        logger.info("Returning from route handler function '{}'".format(f.__name__))
        return result

    return wrapper
