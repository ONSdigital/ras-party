from unittest.mock import patch, Mock

from ras_party.controllers.gov_uk_notify import GovUKNotify
from ras_party.controllers.ras_error import RasNotifyError
from test.party_client import PartyTestClient


class TestParties(PartyTestClient):
    """ Gov uk notify test class"""

    def test_notify_calls_send_message_notification(self):

        # Given a mocked gov.uk notify and response
        mock_response = {'id': 'notification id'}
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(return_value=mock_response)

        with patch('ras_party.controllers.gov_uk_notify.NotificationsAPIClient', return_value=notify_patch):
            notify = GovUKNotify()
            # When an email is sent
            notify.send_message('email', 'template_id')
            # Then send_email_notification is called
            notify_patch.send_email_notification.assert_called_once_with(email_address='email',
                                                                         personalisation=None,
                                                                         reference=None,
                                                                         template_id='template_id')

    def test_notify_exception_is_translated_to_ras_exception(self):

        # Given a mocked gov.uk notify and exception
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(side_effect=Exception)

        with patch('ras_party.controllers.gov_uk_notify.NotificationsAPIClient', return_value=notify_patch):
            # When an email is sent
            notify = GovUKNotify()
            # Then a RasNotifyError is raised
            with self.assertRaises(RasNotifyError):
                notify.send_message('email', 'template_id')
