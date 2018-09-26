class RasNotifyError(Exception):

    def __init__(self, description=None, error=None):
        self.description = description
        self.error = error
