from flask import current_app
from notifications_python_client import NotificationsAPIClient
from structlog import get_logger

from ras_party.support.ras_error import RasNotifyError

log = get_logger()


class GovUKNotify:
    """ Gov uk notify class"""

    CLIENT_CLASS = NotificationsAPIClient

    def __init__(self):
        notify_service = current_app.config.dependency['notify-service']
        notify_keys = 'key-name-{}-{}'.format(notify_service['service_id'],
                                              notify_service['api_key'])
        self.notifications_client = self.CLIENT_CLASS(notify_keys)

    def send_message(self, email, template_id, personalisation=None, reference=None):
        """
        Send message to gov.uk notify
        :param email: email address of recipient
        :param template_id: the template id on gov.uk notify to use
        :param personalisation: placeholder values in the template
        :param reference: reference to generated if not using Notify's id
        :rtype: 201 if success
        """
        try:
            response = self.notifications_client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=personalisation,
                reference=reference)

            log.info('Message sent to GOV.UK Notify with notification id {}'.format(response['id']))

        except Exception as e:
            msg = 'Unable to send message to GOV.UK Notify  ' + str(e)
            raise RasNotifyError(msg, status_code=500)
