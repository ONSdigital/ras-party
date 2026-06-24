from concurrent.futures import TimeoutError
from unittest.mock import MagicMock, patch

from flask import current_app
from flask_testing import TestCase
from google.api_core.client_options import ClientOptions

from ras_party.controllers.notify_gateway import NotifyGateway
from ras_party.exceptions import RasNotifyError
from run import create_app


class TestNotifyGatewayUnit(TestCase):
    """
    Unit tests for NotifyGateway controller

    Note: Even though these are unit tests, we have a create_app function to let us easily access the config
    as a dictionary as it's difficult to do otherwise.
    """

    @staticmethod
    def create_app():
        return create_app("TestingConfig")

    def test_get_template_with_fake_template_name(self):
        # Given a mocked notify gateway

        notify = NotifyGateway(current_app.config)
        # When given a fake template name
        template_name = "fake_name"
        # Then a key error is raised
        with self.assertRaises(KeyError):
            notify._get_template_id(template_name)

    def test_request_to_notify_with_pubsub_no_personalisation(self):
        """Tests what is sent to pubsub when no personalisation is added"""
        publisher = MagicMock()
        publisher.topic_path.return_value = "projects/test-project-id/topics/ras-rm-notify-test"
        # Given a mocked notify gateway
        notify = NotifyGateway(current_app.config)
        notify.publisher = publisher
        result = notify.request_to_notify("test@email.com", "notify_account_locked")
        data = (
            b'{"notify": {"email_address": "test@email.com", '
            b'"template_id": "account_locked_id", "personalisation": {}}}'
        )

        publisher.publish.assert_called_with("projects/test-project-id/topics/ras-rm-notify-test", data=data)
        publisher.publish.assert_called()
        self.assertIsNone(result)

    def test_request_to_notify_with_pubsub_with_personalisation(self):
        """Tests what is sent to pubsub when personalisation is added"""
        publisher = MagicMock()
        publisher.topic_path.return_value = "projects/test-project-id/topics/ras-rm-notify-test"
        # Given a mocked notify gateway
        notify = NotifyGateway(current_app.config)
        notify.publisher = publisher
        personalisation = {"first_name": "testy", "last_name": "surname"}
        result = notify.request_to_notify("test@email.com", "notify_account_locked", personalisation)
        data = (
            b'{"notify": {"email_address": "test@email.com", "template_id": "account_locked_id",'
            b' "personalisation": {"first_name": "testy", "last_name": "surname"}}}'
        )
        publisher.publish.assert_called()
        publisher.publish.assert_called_with("projects/test-project-id/topics/ras-rm-notify-test", data=data)
        self.assertIsNone(result)

    def test_request_to_notify_with_pubsub_timeout_error(self):
        """Tests if the future.result() raises a TimeoutError then the function raises a RasNotifyError"""
        future = MagicMock()
        future.result.side_effect = TimeoutError("bad")
        publisher = MagicMock()
        publisher.publish.return_value = future

        # Given a mocked notify gateway
        notify = NotifyGateway(current_app.config)
        notify.publisher = publisher
        with self.assertRaises(RasNotifyError):
            notify.request_to_notify("test@email.com", "notify_account_locked")

    def test_create_publisher_with_api_endpoint(self):
        notify = NotifyGateway(current_app.config)
        notify.pubsub_api_endpoint = "europe-west2-pubsub.googleapis.com:443"

        with patch("ras_party.controllers.notify_gateway.pubsub_v1.PublisherClient") as publisher_client:
            notify._create_publisher()

        publisher_client.assert_called_once()
        client_options = publisher_client.call_args.kwargs.get("client_options")
        self.assertIsInstance(client_options, ClientOptions)
        self.assertEqual(client_options.api_endpoint, "europe-west2-pubsub.googleapis.com:443")
