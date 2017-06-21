from flask import make_response, jsonify


def translate_exceptions(func):
    # TODO: ultimately we don't want to expose error details to the caller, so should possible map expected
    # TODO: errors to something more friendly, and fall back to a generic 500 on unexpected errors
    def function_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return make_response(jsonify({'errors': str(e)}), 500)
    return function_wrapper
