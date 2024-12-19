class RasNotifyError(Exception):
    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k, v in kwargs.items():
            self.__dict__[k] = v


class ServiceUnavailableException(Exception):
    status_code = 500

    def __init__(self, errors, status_code=None):
        self.errors = errors if isinstance(errors, list) else [errors]
        self.status_code = status_code

    def to_dict(self):
        return {"errors": self.errors}
