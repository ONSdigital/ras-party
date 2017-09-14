from notifications_python_client import NotificationsAPIClient
from structlog import get_logger

from ras_party.support.ras_error import RasNotifyError

log = get_logger()


class GovUkNotify:
    """ Gov uk notify class"""

    CLIENT_CLASS = NotificationsAPIClient

    def __init__(self, config):
        self.config = config
        self.notify_config = config.dependency['notify-service']
        notify_keys = 'key-name-{}-{}'.format(self.notify_config['service_id'],
                                              self.notify_config['api_key'])
        self.notifications_client = self.CLIENT_CLASS(notify_keys)

    def _send_message(self, email, template_id, personalisation=None, reference=None):
        """
        Send message to gov.uk notify
        :param email: email address of recipient
        :param template_id: the template id on gov.uk notify to use
        :param personalisation: placeholder values in the template
        :param reference: reference to generated if not using Notify's id
        :rtype: 201 if success
        """

        if not self.config.feature.send_email_to_gov_notify:
            log.info("Notification not sent. GOV.UK Notify is disabled.")
            return

        try:
            response = self.notifications_client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=personalisation,
                reference=reference)

            log.info('Notification id {} sent via GOV.UK Notify.'.format(response['id']))

        except Exception as e:
            msg = 'There was a problem sending a notification via GOV.UK Notify  ' + str(e)
            raise RasNotifyError(msg, status_code=500)

    def verify_email(self, email, personalisation=None, reference=None):
        template_id = self.notify_config['email_verification_template']
        self._send_message(email, template_id, personalisation, reference)

    def request_password_change(self, email, personalisation=None, reference=None):
        template_id = self.notify_config['request_password_change_template']
        self._send_message(email, template_id, personalisation, reference)

    def confirm_password_change(self, email, personalisation=None, reference=None):
        template_id = self.notify_config['confirm_password_change_template']
        self._send_message(email, template_id, personalisation, reference)
