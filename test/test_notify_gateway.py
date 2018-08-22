from flask import current_app

from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.exceptions import RasNotifyError
from ras_party.support.requests_wrapper import Requests
from test.mocks import MockRequests
from test.party_client import PartyTestClient


class TestNotifyGateway(PartyTestClient):
    """ Notify gateway test class"""
    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

    def test_notify_sends_notification_with_basic_message(self):
        # Given a mocked notify gateway and response
        self.mock_requests.post.response_payload = '{"id": "notification id"}'

        notify = NotifyGateway(current_app.config)
        # When an email is sent
        notify.verify_email('email')
        # Then send_email_notification is called

        expected_data = {"emailAddress": "email"}

        expected_request = {"auth": (current_app.config['SECURITY_USER_NAME'],
                                     current_app.config['SECURITY_USER_PASSWORD']),
                            "timeout": 99, "json": expected_data}

        self.mock_requests.post.assert_called_with(
            "http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/email_verification_id",
            expected_request)

    def test_notify_sends_notification_with_extended_message(self):
        # Given a mocked notify gateway and response
        self.mock_requests.post.response_payload = '{"id": "notification id"}'

        notify = NotifyGateway(current_app.config)
        # When an email is sent
        notify.request_password_change("email", personalisation="personalised message", reference="reference")
        # Then send_email_notification is called
        expected_data = {"emailAddress": "email", "personalisation": "personalised message", "reference": "reference"}
        expected_request = {"auth": (current_app.config['SECURITY_USER_NAME'],
                                     current_app.config['SECURITY_USER_PASSWORD']),
                            "timeout": 99, "json": expected_data}

        self.mock_requests.post.assert_called_with(
            "http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/request_password_change_id",
            expected_request)

    def test_notify_exception_is_translated_to_ras_exception(self):
        # Given a mocked gov.uk notify and exception
        def mock_post_notify(*args, **kwargs):
            return Exception
        self.mock_requests.post = mock_post_notify

        # When an email is sent
        notify = NotifyGateway(current_app.config)
        # Then a RasNotifyError is raised
        with self.assertRaises(RasNotifyError):
            notify.confirm_password_change('email')
