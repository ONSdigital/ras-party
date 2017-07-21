from requests.models import Response
from unittest.mock import patch, Mock

from ras_party.controllers.gov_uk_notify import GovUKNotify
from ras_party.controllers.ras_error import RasNotifyError
from test.party_client import PartyTestClient


class TestParties(PartyTestClient):
    """ Gov uk notify test class"""

    def test_notify(self):

        # Given a mocked gov.uk notify and response
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.id = 'notification id'
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(return_value=mock_response)

        with patch('ras_party.controllers.gov_uk_notify.NotificationsAPIClient', return_value=notify_patch):
            notify = GovUKNotify()
            # When a email is sent
            response = notify.send_message('email', 'template_id')
            # Then a message is created
            self.assertEquals(response, 201)

    def test_notify_exception(self):

        # Given a mocked gov.uk notify and exception
        notify_patch = Mock()
        notify_patch.send_email_notification = Mock(side_effect=Exception)

        with patch('ras_party.controllers.gov_uk_notify.NotificationsAPIClient', return_value=notify_patch):
            # When an email is sent
            notify = GovUKNotify()
            # Then a RasNotifyError is raised
            with self.assertRaises(RasNotifyError):
                notify.send_message('email', 'template_id')
