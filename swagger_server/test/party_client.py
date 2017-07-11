import json

import yaml
from flask import current_app
from flask_testing import TestCase
from ons_ras_common.ras_config import ras_config

from run import create_app
from swagger_server.controllers import controller
from swagger_server.models.models import Business, Respondent, BusinessRespondent
from swagger_server.test.fixtures.config import test_config


def businesses():
    return current_app.db.session.query(Business).all()


def respondents():
    return current_app.db.session.query(Respondent).all()


def business_respondent_associations():
    return current_app.db.session.query(BusinessRespondent).all()


class PartyTestClient(TestCase):
    config_data = yaml.load(test_config)
    config = ras_config.make(config_data)

    def create_app(self):
        app = create_app(self.config)
        return app

    def post_to_parties(self, payload, expected_status):
        response = self.client.open('/party-api/v1/parties',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.data)

    def post_to_businesses(self, payload, expected_status):
        response = self.client.open('/party-api/v1/businesses',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_businesses_x(self, payload, expected_status):
        response = controller.businesses_post(payload)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_respondents(self, payload, expected_status):
        response = self.client.open('/party-api/v1/respondents',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_party_by_ref(self, party_type, ref, expected_status=200):
        response = self.client.open('/party-api/v1/parties/type/{}/ref/{}'.format(party_type, ref),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_party_by_id(self, party_type, id, expected_status=200):
        response = self.client.open('/party-api/v1/parties/type/{}/id/{}'.format(party_type, id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_id(self, id, expected_status=200):
        response = self.client.open('/party-api/v1/businesses/id/{}'.format(id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_ref(self, ref, expected_status=200):
        response = self.client.open('/party-api/v1/businesses/ref/{}'.format(ref),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondent_by_id(self, id, expected_status=200):
        response = self.client.open('/party-api/v1/respondents/id/{}'.format(id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))
