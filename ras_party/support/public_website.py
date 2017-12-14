from ras_party.support.verification import generate_email_token


class PublicWebsite:

    def __init__(self, config):
        self.config = config
        self.website_uri = config['RAS_PUBLIC_WEBSITE_URL']

    def reset_password_url(self, email):
        return f'{self.website_uri}/passwords/reset-password/{self._generate_token(email)}'

    def activate_account_url(self, email):
        return f'{self.website_uri}/register/activate-account/{self._generate_token(email)}'

    def _generate_token(self, email):
        return generate_email_token(email, self.config)
