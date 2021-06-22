from flask import current_app

from ras_party.support.verification import generate_email_token


class PublicWebsite:

    def __init__(self):
        self.website_uri = current_app.config['FRONTSTAGE_URL']

    def reset_password_url(self, email):
        return f'{self.website_uri}/passwords/reset-password/{self._generate_token(email)}'

    def activate_account_url(self, email):
        return f'{self.website_uri}/register/activate-account/{self._generate_token(email)}'

    def confirm_account_email_change_url(self, email):
        return f'{self.website_uri}/my-account/confirm-account-email-change/{self._generate_token(email)}'

    def share_survey(self, batch_number):
        return f'{self.website_uri}/my-account/' \
               f'share-surveys/accept-share-surveys/{self._generate_token(str(batch_number))}'

    def transfer_survey(self, batch_number):
        return f'{self.website_uri}/my-account/' \
               f'transfer-surveys/accept-transfer-surveys/{self._generate_token(str(batch_number))}'

    def resend_share_survey(self, batch_number):
        return f'{self.website_uri}/my-account/share-surveys'

    def resend_transfer_survey(self, batch_number):
        return f'{self.website_uri}/my-account/transfer-surveys'

    @staticmethod
    def _generate_token(email):
        return generate_email_token(email)
