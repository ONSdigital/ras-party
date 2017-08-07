from flask import current_app
from notifications_python_client import NotificationsAPIClient
from structlog import get_logger

from ras_party.controllers.ras_error import RasNotifyError

log = get_logger()

# TODO: Consider removing this class. It's not needed and adds little value.
class GovUKNotify:
    """ Gov uk notify class"""

    def __init__(self):
        # TODO: This init does not work as intended. It generates an exception if the service is switched off and a call
        # from another function tries to send an email.
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
            log.error(msg)
            raise RasNotifyError(msg, status_code=400)

        # TODO Use celery to handle async requests for sending emails. This should stop any possible rate limit errors: see http://flask.pocoo.org/docs/0.12/patterns/celery/
        if not response.status_code == 201:
            if response.status_code == 429:
                log.error("Sending an email to the gov.notify service has been rate limited")
                msg = "Sending emails has been rate limited"
                raise RasNotifyError(msg)

            elif response.status_code == 400:
                log.error("Sending an email to the recipient: {} is not allowed by the gov.notify service".format(email))
                msg = "Emails to this recipient are not allowed by the email provider"
                raise RasNotifyError(msg)

            else:
                log.error("An unknown error occured in sending an email to the recipient: {}".format(email))
                msg = "An unknown error has occured from the email provider"
                raise RasNotifyError(msg)

        return response.status_code
