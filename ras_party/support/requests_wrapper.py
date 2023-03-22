import requests
from flask import current_app


class Requests:
    _lib = requests

    @staticmethod
    def auth():
        return current_app.config["SECURITY_USER_NAME"], current_app.config["SECURITY_USER_PASSWORD"]

    @classmethod
    def get(cls, *args, **kwargs):
        try:
            auth = kwargs.pop("auth")
        except KeyError:
            auth = cls.auth()
        return cls._lib.get(*args, auth=auth, timeout=20, **kwargs)

    @classmethod
    def put(cls, *args, **kwargs):
        try:
            auth = kwargs.pop("auth")
        except KeyError:
            auth = cls.auth()
        return cls._lib.put(*args, auth=auth, timeout=20, **kwargs)

    @classmethod
    def post(cls, *args, **kwargs):
        try:
            auth = kwargs.pop("auth")
        except KeyError:
            auth = cls.auth()
        return cls._lib.post(*args, auth=auth, timeout=20, **kwargs)
