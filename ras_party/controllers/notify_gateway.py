import logging

import structlog

from ras_party.exceptions import RasNotifyError
from ras_party.support.requests_wrapper import Requests
from urllib import parse as urlparse

logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyGateway:
    """ Client for Notify gateway"""

    def __init__(self, config):
        self.config = config
        self.notify_url = config['RAS_NOTIFY_SERVICE_URL']
        self.email_verification_template = config['RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE']
        self.request_password_change_template = config['RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE']
        self.confirm_password_change_template = config['RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE']

    def _send_message(self, email, template_id, personalisation=None, reference=None):
        """
        Send message to gov.uk notify wrapper
        :param email: email address of recipient
        :param template_id: the template id on gov.uk notify to use
        :param personalisation: placeholder values in the template
        :param reference: reference to be generated if not using Notify's id
        :rtype: 201 if success
        """

        if not self.config['SEND_EMAIL_TO_GOV_NOTIFY']:
            logger.info("Notification not sent. Notify is disabled.")
            return

        try:
            notification = {
                "emailAddress": email,
            }
            if personalisation:
                notification.update({"personalisation": personalisation})
            if reference:
                notification.update({"reference": reference})

            url = urlparse.urljoin(self.notify_url, str(template_id))

            response = Requests.post(url, json=notification)

            logger.info('Notification id sent via Notify-Gateway to GOV.UK Notify.', id=response.json()["id"])

        except Exception as e:
            raise RasNotifyError("There was a problem sending a notification via Notify-Gateway to GOV.UK Notify",
                                 error=e)

    def verify_email(self, email, personalisation=None, reference=None):
        template_id = self.email_verification_template
        self._send_message(email, template_id, personalisation, reference)

    def request_password_change(self, email, personalisation=None, reference=None):
        template_id = self.request_password_change_template
        self._send_message(email, template_id, personalisation, reference)

    def confirm_password_change(self, email, personalisation=None, reference=None):
        template_id = self.confirm_password_change_template
        self._send_message(email, template_id, personalisation, reference)
