from flask import current_app
from notifications_python_client import NotificationsAPIClient
from structlog import get_logger

from ras_party.controllers.ras_error import RasNotifyError

log = get_logger()


class GovUKNotify:
    """ Gov uk notify class"""

    def __init__(self):

        notify_service = current_app.config.dependency['gov-uk-notify-service']
        notify_keys = 'key-name-{}-{}'.format(notify_service['gov_notify_service_id'],
                                              notify_service['gov_notify_api_key'])
        self.notifications_client = NotificationsAPIClient(notify_keys)

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

            log.info('Message sent to gov.uk notify with notification id {}'.format(response['id']))

        except Exception as e:
            msg = 'Gov uk notify can not send the message' + str(e)
            raise RasNotifyError(msg, status_code=500)
