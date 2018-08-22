from flask import current_app

from ras_party.clients import http


class OauthClient:
    def __init__(self):
        self.service = current_app.config['RAS_OAUTH_SERVICE']
        self.client_id = current_app.config['RAS_OAUTH_CLIENT_ID']
        self.client_secret = current_app.config['RAS_OAUTH_CLIENT_SECRET']

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
        return http().post(self.admin_url, auth=basic_auth, data=payload)

    def update_account(self, **kwargs):
        basic_auth = (self.client_id, self.client_secret)
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        payload.update(kwargs)
        return http().put(self.admin_url, auth=basic_auth, data=payload)
