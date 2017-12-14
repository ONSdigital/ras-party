from ras_party.support.requests_wrapper import Requests


class OauthClient:
    def __init__(self, config):
        self.service = config['RAS_OAUTH_SERVICE']
        self.client_id = config['RAS_OAUTH_CLIENT_ID']
        self.client_secret = config['RAS_OAUTH_CLIENT_SECRET']

    @property
    def admin_url(self):
        return f'{self.service}/api/account/create'

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
