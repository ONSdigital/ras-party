from ras_party.support.requests_wrapper import Requests


class OauthClient:
    def __init__(self, config):
        self.service_config = config.dependency['oauth2-service']
        self.client_id = self.service_config['client_id']
        self.client_secret = self.service_config['client_secret']

    @property
    def admin_url(self):
        sc = self.service_config
        return '{}://{}:{}/api/account/create'.format(sc['scheme'], sc['host'], sc['port'])

    def create_account(self, username, password):
        payload = {
            'username': username,
            'password': password,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        basic_auth = (self.client_id, self.client_secret)
        return Requests.post(self.admin_url, auth=basic_auth, data=payload)

    def update_account(self, **kwargs):
        basic_auth = (self.client_id, self.client_secret)
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        payload.update(kwargs)
        return Requests.put(self.admin_url, auth=basic_auth, data=payload)
