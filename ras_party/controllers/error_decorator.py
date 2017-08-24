from functools import wraps

import structlog
from flask import current_app
from ras_common_utils.ras_error.ras_error import RasError
from requests import HTTPError


log = structlog.get_logger()


def translate_exceptions(f):
    # TODO: ultimately we don't want to expose error details to the caller, so should possible map expected
    # TODO: errors to something more friendly, and fall back to a generic 500 on unexpected errors
    @wraps(f)
    def wrapper(*args, **kwargs):
        # TODO: log the stack-trace
        try:
            return f(*args, **kwargs)
        except RasError as e:
            log.error(e.to_dict())
            raise
        except HTTPError as e:
            detail = e.response.json().get('detail', "No further detail.")
            raise RasError([str(e), detail])
        except Exception as e:
            log.error(str(e))
            if current_app.config.feature.translate_exceptions:
                raise RasError(str(e))
            else:
                raise
    return wrapper
