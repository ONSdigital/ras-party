import structlog
from flask import make_response, jsonify, current_app


logger = structlog.get_logger()


def translate_exceptions(func):
    # TODO: ultimately we don't want to expose error details to the caller, so should possible map expected
    # TODO: errors to something more friendly, and fall back to a generic 500 on unexpected errors
    def function_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # TODO: log the stack-trace
            logger.error(e)
            if current_app.config.feature.get('translate_exceptions'):
                return make_response(jsonify({'errors': str(e)}), 500)
            else:
                raise
    return function_wrapper
