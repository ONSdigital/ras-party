
class RasError(Exception):
    """
    RAS domain-specific errors. The ctor accepts either a string describing the error, or a list of strings
    if there are multiple lines of description.

    status_code defaults to 500, and is overridden at the point of raising by providing a custom status_code value.
    """
    status_code = 500

    def __init__(self, errors, status_code=None):
        self.errors = errors if type(errors) is list else [errors]
        self.status_code = status_code or RasError.status_code

    def to_dict(self):
        return {'errors': self.errors}


class RasDatabaseError(RasError):
    pass


class RasNotifyError(RasError):
    pass
