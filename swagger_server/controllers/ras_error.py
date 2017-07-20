class RasError(Exception):
    status_code = 500

    def __init__(self, *args, status_code=None):
        super().__init__(*args)
        self.status_code = status_code or RasError.status_code

    def to_dict(self):
        return {'errors': [str(self)]}


class RasDatabaseError(RasError):
    pass


class RasNotifyError(RasError):
    pass
