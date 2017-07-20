
class RasError(Exception):
    status_code = 500
    #TODO A RasError will need to deal with more than just a HTTP 500. e.g. Party Service registers a user who has a duplicate
    # user id. It will have to convey this to the calling party (ras_frontstage) so that it can deal correclty with this issue.

    def __init__(self, errors, status_code=None):
        self.errors = errors if type(errors) is list else [errors]
        self.status_code = status_code or RasError.status_code

    def to_dict(self):
        return {'errors': self.errors}


class RasDatabaseError(RasError):
    pass
