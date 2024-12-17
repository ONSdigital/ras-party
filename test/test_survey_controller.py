import unittest
from unittest.mock import patch

from requests import ConnectionError, HTTPError, Timeout
from requests.models import Response

from ras_party.controllers.survey_controller import get_surveys_details
from ras_party.exceptions import ServiceUnavailableException
from run import create_app


class TestConversationController(unittest.TestCase):

    def setUp(self):
        self.app = create_app("TestingConfig")

    def test_get_surveys_details(self):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = (
            b'[{"id": "41320b22-b425-4fba-a90e-718898f718ce", "shortName": "AIFDI", "longName": '
            b'"Annual Inward Foreign Direct Investment Survey", "surveyRef": "062"}]'
        )

        with patch("requests.get", return_value=mock_response):
            with self.app.app_context():
                surveys_details = get_surveys_details()

        self.assertEqual(
            surveys_details,
            {
                "41320b22-b425-4fba-a90e-718898f718ce": {
                    "short_name": "AIFDI",
                    "long_name": "Annual Inward Foreign Direct Investment Survey",
                    "ref": "062",
                }
            },
        )

    def test_get_surveys_details_connection_error(self):
        with patch("requests.get", side_effect=ConnectionError):
            with self.app.app_context():
                with self.assertRaises(ServiceUnavailableException):
                    get_surveys_details()

    def test_get_surveys_details_timeout(self):
        with patch("requests.get", side_effect=Timeout):
            with self.app.app_context():
                with self.assertRaises(ServiceUnavailableException):
                    get_surveys_details()

    def test_get_surveys_details_http_error(self):
        with patch("requests.get", side_effect=HTTPError):
            with self.app.app_context():
                with self.assertRaises(HTTPError):
                    get_surveys_details()
