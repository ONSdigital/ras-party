from ras_party.support.verification import generate_email_token


class PublicWebsite:

    def __init__(self, config):
        self.config = config
        self.website_config = config.dependency['public-website']

    @property
    def scheme(self):
        return self.website_config['scheme']

    @property
    def host(self):
        return self.website_config['host']

    @property
    def port(self):
        return self.website_config['port']

    def forgot_password_url(self, email):
        return '{}://{}/passwords/forgot-password/{}'.format(self.scheme, self.host, self._generate_token(email))

    def activate_account_url(self, email):
        return '{}://{}/register/activate-account/{}'.format(self.scheme, self.host, self._generate_token(email))

    def _generate_token(self, email):
        return generate_email_token(email, self.config)
