from unittest.mock import patch

from requests import Request, RequestException, Response

from ras_party.error_handlers import client_error, exception_error, http_error, ras_error
from ras_party.exceptions import ClientError, RasError
from test.party_client import PartyTestClient


class TestErrorHandlers(PartyTestClient):

    def test_uncaught_client_error_handler_will_log_exception(self):
        # Given
        error = ClientError(errors=['some error'], status=400)

        with patch('ras_party.error_handlers.logger') as logger:
            # When
            client_error(error)
            # Then
            logger.info.assert_called_once_with('Client error', errors={'errors': ['some error']},
                                                status=400)

    def test_uncaught_ras_error_handler(self):
        # Given
        error = RasError(errors=['some error'], status=418)
        # When
        response = ras_error(error)

        # Then
        self.assertEqual(response.status_code, 418)

    def test_uncaught_ras_error_handler_will_log_exception(self):
        # Given
        error = RasError(errors=['some error'], status=418)

        with patch('ras_party.error_handlers.logger') as logger:
            # When
            ras_error(error)

            # Then
            logger.exception.assert_called_once_with('Uncaught exception', errors={'errors': ['some error']},
                                                     status=418)

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
            logger.exception.assert_called_once_with('Uncaught exception',
                                                     errors={'errors': {'method': 'GET', 'url': 'http://localhost'}},
                                                     status=500)

    def test_uncaught_exception_handler(self):
        # Given
        error = Exception()
        # When
        response = exception_error(error)

        # Then
        self.assertEqual(response.status_code, 500)

    def test_uncaught_exception_handler_will_log_exception(self):
        # Given
        error = Exception()

        with patch('ras_party.error_handlers.logger') as logger:
            # When
            exception_error(error)

            # Then
            logger.exception.assert_called_once_with('Uncaught exception', status=500)
