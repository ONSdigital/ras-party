from structlog import get_logger

from ras_party.support.ras_error import RasNotifyError
from ras_party.support.requests_wrapper import Requests
from urllib import parse as urlparse

log = get_logger()


class GovUkNotify:
    """ Gov uk notify class"""

    def __init__(self, config):
        self.config = config
        self.notify_config = config.dependency['notify-service']

    def _send_message(self, email, template_id, personalisation=None, reference=None):
        """
        Send message to gov.uk notify wrapper
        :param email: email address of recipient
        :param template_id: the template id on gov.uk notify to use
        :param personalisation: placeholder values in the template
        :param reference: reference to be generated if not using Notify's id
        :rtype: 201 if success
        """

        if not self.config.feature.send_email_to_gov_notify:
            log.info("Notification not sent. Notify is disabled.")
            return

        try:
            notification = {
                "emailAddress": email,
            }
            if personalisation:
                notification.update({"personalisation": personalisation})
            if reference:
                notification.update({"reference": reference})

            url = urlparse.urljoin(str(self.notify_config['url']), str(template_id))

            response = Requests.post(url, json=notification)

            log.info('Notification id {} sent via RM Notify-Gateway to GOV.UK Notify.'
                     .format(response.json()["id"]))

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
