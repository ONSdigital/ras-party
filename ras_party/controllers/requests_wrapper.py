import requests
from flask import current_app


class Requests:

    _lib = requests

    @staticmethod
    def get_timeout():
        return int(current_app.config['REQUESTS_GET_TIMEOUT'])

    @staticmethod
    def post_timeout():
        return int(current_app.config['REQUESTS_POST_TIMEOUT'])

    @staticmethod
    def auth():
        return current_app.config['SECURITY_USER_NAME'], current_app.config['SECURITY_USER_PASSWORD']

    @classmethod
    def get(cls, *args, **kwargs):
        return cls._lib.get(*args, **kwargs, auth=cls.auth(), timeout=cls.get_timeout())

    @classmethod
    def put(cls, *args, **kwargs):
        return cls._lib.put(*args, **kwargs, auth=cls.auth(), timeout=cls.post_timeout())

    @classmethod
    def post(cls, *args, **kwargs):
        return cls._lib.post(*args, **kwargs, auth=cls.auth(), timeout=cls.post_timeout())
