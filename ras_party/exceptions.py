
class RasError(Exception):

    status_code = 500

    def __init__(self, errors, status=None, **kwargs):
        self.errors = errors if isinstance(errors, list) else [errors]
        self.status_code = status or RasPartyError.status_code
        self.kwargs = kwargs

    def to_dict(self):
        return {'errors': self.errors}


class RasDatabaseError(RasError):
    pass


class RasPartyError(RasError):
    pass


class RasNotifyError(RasError):
    pass
