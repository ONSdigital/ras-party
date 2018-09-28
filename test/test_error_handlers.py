from unittest.mock import patch

from flask import request
from requests import Request, RequestException, Response
from werkzeug.exceptions import NotFound

from ras_party.error_handlers import http_error, http_exception_handler, exception_error
from test.party_client import PartyTestClient


class TestErrorHandlers(PartyTestClient):

    def test_uncaught_request_exception_handler(self):
        # Given
        response = Response()
        response.status_code = 418
        error = RequestException(request=Request(method='GET', url='http://localhost'), response=response)
        # When
        response = http_error(error)

        # Then
        self.assertEqual(response.status_code, 418)

    def test_uncaught_request_exception_handler_will_log_exception(self):
        # Given
        error = RequestException(request=Request(method='GET', url='http://localhost'))

        with patch('ras_party.error_handlers.logger') as logger:
            # When
            http_error(error)

            # Then
            logger.exception.assert_called_once_with('Error requesting another service',
                                                     errors={'errors': {'method': 'GET', 'url': 'http://localhost'}},
                                                     status=500,
                                                     url=request.url)

    def test_uncaught_http_exception_handler(self):
        # Given
        error = NotFound("test NotFound raised")
        # When
        response = http_exception_handler(error)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual("test NotFound raised", response.json['description'])

    def test_uncaught_exception_handler(self):
        # Given
        error = Exception()
        # When
        response = exception_error(error)

        # Then
        self.assertEqual(response.status_code, 500)

    def test_uncaught_exception_handler_will_log_exception(self):
        # Given
        error = Exception("Test exception raised")

        with patch('ras_party.error_handlers.logger') as logger:
            # When
            exception_error(error)

            # Then
            logger.exception.assert_called_once_with('Uncaught exception', exc_info=error, status=500)
