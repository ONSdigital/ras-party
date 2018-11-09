class RasNotifyError(Exception):

    def __init__(self, description=None, error=None, **kwargs):
        self.description = description
        self.error = error
        for k,v in kwargs.items():
            self.__dict__[k] = v
