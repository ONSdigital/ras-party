from unittest.mock import Mock

from flask import current_app

from ras_party.controllers.gov_uk_notify import GovUkNotify
from ras_party.support.ras_error import RasNotifyError
from test.party_client import PartyTestClient


class TestParties(PartyTestClient):
    """ Gov uk notify test class"""

    def test_notify_calls_send_message_notification(self):

        # Given a mocked gov.uk notify and response
        mock_response = {'id': 'notification id'}
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(return_value=mock_response)

        GovUkNotify.CLIENT_CLASS = Mock(return_value=notify_patch)

        notify = GovUkNotify(current_app.config)
        # When an email is sent
        notify.verify_email('email')
        # Then send_email_notification is called
        notify_patch.send_email_notification.assert_called_once_with(email_address='email',
                                                                     personalisation=None,
                                                                     reference=None,
                                                                     template_id='email_verification_id')

    def test_notify_exception_is_translated_to_ras_exception(self):

        # Given a mocked gov.uk notify and exception
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(side_effect=Exception)

        GovUkNotify.CLIENT_CLASS = Mock(return_value=notify_patch)

        # When an email is sent
        notify = GovUkNotify(current_app.config)
        # Then a RasNotifyError is raised
        with self.assertRaises(RasNotifyError):
            notify.verify_email('email')
