import json
import logging
from urllib import parse as urlparse

import structlog

from ras_party.exceptions import RasNotifyError
from ras_party.support.requests_wrapper import Requests
from google.cloud import pubsub_v1


logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyGateway:
    """ Client for Notify gateway"""

    def __init__(self, config):
        self.config = config
        self.notify_url = config['NOTIFY_URL']
        self.email_verification_template = config['NOTIFY_EMAIL_VERIFICATION_TEMPLATE']
        self.request_password_change_template = config['NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE']
        self.confirm_password_change_template = config['NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE']
        self.notify_account_locked = config['NOTIFY_ACCOUNT_LOCKED_TEMPLATE']

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
            ref = reference if reference else 'reference_unknown'
            raise RasNotifyError("There was a problem sending a notification to Notify-Gateway to GOV.UK Notify",
                                 error=e, reference=ref)

    def _send_message_via_pubsub(self, email, template_id, personalisation):
        """Sends an email via pubsub topic

        :param email: Email address to send the email too
        :type email: str
        :param template_id: A uuid of the template_id to be used in gov notify
        :type template_id: str
        :param personalisation: A dictionary containing
        :type personalisation: dict
        :return:
        """
        if not self.config['SEND_EMAIL_TO_GOV_NOTIFY']:
            logger.info("Notification not sent. Notify is disabled.")
            return

        try:
            # Need to double check notify, but I think reference can be dropped.  I think it was used for logging?
            # if reference:
            #     notification.update({"reference": reference})

            payload = {
                'notify': {
                    'email_address': email,
                    'template_id': template_id,
                    'personalisation': {}
                }
            }
            if personalisation:
                payload['notify']['personalisation'] = personalisation

            payload_str = json.dumps(payload)
            payload_bytes = payload_str.encode()

            publisher = pubsub_v1.PublisherClient()
            project_id = self.config['GCP_PROJECT_ID']
            topic_id = self.config['NOTIFY_PUBSUB_TOPIC']
            # The `topic_path` method creates a fully qualified identifier
            # in the form `projects/{project_id}/topics/{topic_id}`
            topic_path = publisher.topic_path(project_id, topic_id)

            future = publisher.publish(topic_path, data=payload_bytes)
            logger.info("Publish result", result=future.result())

        except Exception as e:
            raise RasNotifyError("There was a problem sending a notification to Notify-Gateway to GOV.UK Notify",
                                 error=e)

    def request_to_notify(self, email, template_name, personalisation=None, reference=None):
        template_id = self._get_template_id(template_name)
        if self.config['USE_PUBSUB_FOR_EMAIL']:
            self._send_message_via_pubsub(email, template_id, personalisation)
        else:
            self._send_message(email, template_id, personalisation, reference)

    def _get_template_id(self, template_name):
        templates = {'notify_account_locked': self.notify_account_locked,
                     'confirm_password_change': self.confirm_password_change_template,
                     'request_password_change': self.request_password_change_template,
                     'email_verification': self.email_verification_template}
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError('Template does not exist')
