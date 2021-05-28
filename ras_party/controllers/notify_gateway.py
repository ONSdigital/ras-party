import json
import logging
from concurrent.futures import TimeoutError

import structlog
from google.cloud import pubsub_v1

from ras_party.exceptions import RasNotifyError

logger = structlog.wrap_logger(logging.getLogger(__name__))


class NotifyGateway:
    """Client for Notify gateway"""

    def __init__(self, config):
        self.config = config
        self.notify_url = config["NOTIFY_URL"]
        self.email_verification_template = config["NOTIFY_EMAIL_VERIFICATION_TEMPLATE"]
        self.request_password_change_template = config[
            "NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE"
        ]
        self.confirm_password_change_template = config[
            "NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE"
        ]
        self.notify_account_locked = config["NOTIFY_ACCOUNT_LOCKED_TEMPLATE"]
        self.verify_account_email_change = config[
            "NOTIFY_VERIFY_ACCOUNT_EMAIL_CHANGE_TEMPLATE"
        ]
        self.confirm_account_email_change = config[
            "NOTIFY_CONFIRM_ACCOUNT_EMAIL_CHANGE_TEMPLATE"
        ]
        self.share_survey_access_new_account = config[
            "SHARE_SURVEY_ACCESS_NEW_ACCOUNT_TEMPLATE"
        ]
        self.share_survey_access_existing_account = config[
            "SHARE_SURVEY_ACCESS_EXISTING_ACCOUNT_TEMPLATE"
        ]
        self.share_survey_access_cancellation = config[
            "SHARE_SURVEY_ACCESS_CANCELLATION_TEMPLATE"
        ]
        self.project_id = self.config["GOOGLE_CLOUD_PROJECT"]
        self.topic_id = self.config["PUBSUB_TOPIC"]
        self.publisher = None

    def _send_message(self, email, template_id, personalisation):
        """Sends an email via pubsub topic

        :param email: Email address to send the email too
        :type email: str
        :param template_id: A uuid of the template_id to be used in gov notify
        :type template_id: str
        :param personalisation: A dictionary containing variables that will be used in the email e.g., names, ru refs
        :type personalisation: dict
        :raises RasNotifyError: Raised on any Exception that occurs.  Most likely will happen if there is an issue when
                                publishing to pubsub.
        :return: None
        """
        bound_logger = logger.bind(
            template_id=template_id, project_id=self.project_id, topic_id=self.topic_id
        )
        bound_logger.info("Sending email via pubsub")
        if not self.config["SEND_EMAIL_TO_GOV_NOTIFY"]:
            bound_logger.info("Notification not sent. Notify is disabled.")
            return

        payload = {
            "notify": {
                "email_address": email,
                "template_id": template_id,
                "personalisation": {},
            }
        }
        if personalisation:
            payload["notify"]["personalisation"] = personalisation

        payload_str = json.dumps(payload)
        if self.publisher is None:
            self.publisher = pubsub_v1.PublisherClient()
        topic_path = self.publisher.topic_path(self.project_id, self.topic_id)

        bound_logger.info("About to publish to pubsub")
        future = self.publisher.publish(topic_path, data=payload_str.encode())

        # It's okay for us to catch a broad Exception here because the documentation for future.result() says it
        # throws either a TimeoutError or an Exception.
        try:
            msg_id = future.result()
            bound_logger.info("Publish succeeded", msg_id=msg_id)
        except TimeoutError as e:
            bound_logger.error("Publish to pubsub timed out", exc_info=True)
            raise RasNotifyError("Publish to pubsub timed out", error=e)
        except Exception as e:  # noqa
            bound_logger.error(
                "A non-timeout error was raised when publishing to pubsub",
                exc_info=True,
            )
            raise RasNotifyError(
                "A non-timeout error was raised when publishing to pubsub", error=e
            )

    def request_to_notify(
        self, email, template_name, personalisation=None, reference=None
    ):
        """
        Sends a message to a pubsub topic which will ultimately result in an email being sent via gov notify

        :param email: Email address to send the email too
        :type email: str
        :param template_name: Name of the template.  This will be translated into a uuid for gov notify to use.
        :type template_name: str
        :param personalisation: A dictionary containing variables that will be used in the email e.g., names, ru refs
        :type personalisation: dict
        :param reference:
        :raises KeyError: Raised if the template name doesn't have a mapping in this class.
        :raises RasNotifyError: Raised on publish errors and any other non-template mapping error.

        """
        template_id = self._get_template_id(template_name)
        self._send_message(email, template_id, personalisation)

    def _get_template_id(self, template_name):
        templates = {
            "notify_account_locked": self.notify_account_locked,
            "confirm_password_change": self.confirm_password_change_template,
            "request_password_change": self.request_password_change_template,
            "email_verification": self.email_verification_template,
            "verify_account_email_change": self.verify_account_email_change,
            "confirm_change_to_account_email": self.confirm_account_email_change,
            "share_survey_access_new_account": self.share_survey_access_new_account,
            "share_survey_access_existing_account": self.share_survey_access_existing_account,
            "share_survey_access_cancellation": self.share_survey_access_cancellation,
        }
        if template_name in templates:
            return templates[template_name]
        else:
            raise KeyError("Template does not exist")
