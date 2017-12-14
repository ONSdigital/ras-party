from ras_party.support.verification import generate_email_token


class PublicWebsite:

    def __init__(self, config):
        self.config = config
        self.website_url = config['RAS_PUBLIC_WEBSITE_URL']

    @property
    def scheme(self):
        return self.config['RAS_PUBLIC_WEBSITE_PROTOCOL']

    @property
    def host(self):
        return self.config['RAS_PUBLIC_WEBSITE_HOST']

    @property
    def port(self):
        return int(self.config['RAS_PUBLIC_WEBSITE_PORT'])

    @property
    def host_port(self):
        if self.scheme == 'https' and self.port == 443:
            result = self.host
        elif self.scheme == 'http' and self.port == 80:
            result = self.host
        else:
            result = f'{self.host}:{self.port}'
        return result

    def reset_password_url(self, email):
        return f'{self.scheme}://{self.host_port}/passwords/reset-password/{self._generate_token(email)}'

    def activate_account_url(self, email):
        return f'{self.scheme}://{self.host_port}/register/activate-account/{self._generate_token(email)}'

    def _generate_token(self, email):
        return generate_email_token(email, self.config)
