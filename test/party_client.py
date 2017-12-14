import base64
import json

from flask import current_app
from flask_testing import TestCase

from logger_config import logger_initial_config
from ras_party.models.models import Business, Respondent, BusinessRespondent, Enrolment
from run import create_app, initialise_db
from test.fixtures import party_schema
from test.fixtures.config import test_config
from test.mocks import MockBusiness


def businesses():
    return current_app.db.session.query(Business).all()


def respondents():
    return current_app.db.session.query(Respondent).all()


def business_respondent_associations():
    return current_app.db.session.query(BusinessRespondent).all()


def enrolments():
    return current_app.db.session.query(Enrolment).all()


class PartyTestClient(TestCase):

    def create_app(self):
        app = create_app('TestingConfig')
        logger_initial_config(service_name='ras-party', log_level=app.config['LOGGING_LEVEL'])
        app.config['PARTY_SCHEMA'] = party_schema.schema
        initialise_db(app)
        return app

    def populate_with_business(self):
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)

    @property
    def auth_headers(self):
        return {
            'Authorization': 'Basic %s' % base64.b64encode(b"username:password").decode("ascii")
        }

    def get_info(self, expected_status=200):
        response = self.client.open('/info', method='GET')
        self.assertStatus(response, expected_status)
        return json.loads(response.get_data(as_text=True))

    def post_to_parties(self, payload, expected_status):
        response = self.client.post('/party-api/v1/parties',
                                    headers=self.auth_headers,
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_businesses(self, payload, expected_status):
        response = self.client.post('/party-api/v1/businesses',
                                    headers=self.auth_headers,
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_respondents(self, payload, expected_status):
        response = self.client.post('/party-api/v1/respondents',
                                    headers=self.auth_headers,
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_email_to_respondents(self, payload, expected_status=200):
        response = self.client.put('/party-api/v1/respondents/email',
                                   headers=self.auth_headers,
                                   data=json.dumps(payload),
                                   content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_party_by_ref(self, party_type, ref, expected_status=200):
        response = self.client.get('/party-api/v1/parties/type/{}/ref/{}'.format(party_type, ref),
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_party_by_id(self, party_type, id, expected_status=200):
        response = self.client.get('/party-api/v1/parties/type/{}/id/{}'.format(party_type, id),
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_id(self, id, expected_status=200, query_string=None):
        response = self.client.get('/party-api/v1/businesses/id/{}'.format(id),
                                   query_string=query_string,
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_ref(self, ref, expected_status=200, query_string=None):
        response = self.client.get('/party-api/v1/businesses/ref/{}'.format(ref),
                                   query_string=query_string,
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondent_by_id(self, id, expected_status=200):
        response = self.client.get('/party-api/v1/respondents/id/{}'.format(id), headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondent_by_email(self, email, expected_status=200):
        response = self.client.get('/party-api/v1/respondents/email/{}'.format(email), headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_email_verification(self, token, expected_status):
        response = self.client.put('/party-api/v1/emailverification/{}'.format(token), headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_verification_email(self, email, expected_status=200):
        response = self.client.get('/party-api/v1/resend-verification-email/{}'.format(email),
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def request_password_change(self, payload, expected_status=200):
        response = self.client.post('/party-api/v1/respondents/request_password_change',
                                    data=json.dumps(payload),
                                    headers=self.auth_headers,
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def change_password(self, token, payload, expected_status=200):
        response = self.client.put('/party-api/v1/respondents/change_password/{}'.format(token),
                                   headers=self.auth_headers, data=json.dumps(payload),
                                   content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def verify_token(self, token, expected_status=200):
        response = self.client.get('/party-api/v1/tokens/verify/{}'.format(token),
                                   headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))
