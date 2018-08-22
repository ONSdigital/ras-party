import requests
from flask import current_app
from flask_zipkin import Zipkin
from requests.auth import HTTPBasicAuth
from requests_middleware import BaseMiddleware, MiddlewareHTTPAdapter

zipkin: Zipkin = None


def http():
    config = current_app.config

    session = requests.Session()
    session.auth = HTTPBasicAuth(config['SECURITY_USER_NAME'], config['SECURITY_USER_PASSWORD'])

    middleware = [
        ZipkinMiddleware(zipkin),
    ]

    adapter = TimeoutMiddlewareHTTPAdapter(
        middlewares=middleware,
        timeout=int(current_app.config['REQUESTS_POST_TIMEOUT'])
    )

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


class ZipkinMiddleware(BaseMiddleware):
    client: Zipkin

    def __init__(self, client):
        self.client = client

    def before_send(self, request, *args, **kwargs):
        request.headers = self.client.create_http_headers_for_new_span().update(request.headers)


class TimeoutMiddlewareHTTPAdapter(MiddlewareHTTPAdapter):
    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        super(MiddlewareHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        return super(MiddlewareHTTPAdapter, self).send(*args, **kwargs)
