import uuid
from unittest.mock import MagicMock, patch

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from ras_common_utils.ras_error.ras_error import RasError
from ras_party.controllers import account_controller
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.verification import generate_email_token
from test.mocks import MockBusiness, MockRequests, MockResponse
from test.party_client import PartyTestClient, businesses, enrolments


class TestParties(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().attributes(source='test_post_valid_business_adds_to_db').as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

    def test_post_valid_party_adds_to_db(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()
        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)

    def test_get_business_by_id_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id)
        self.assertEqual(len(response.items()), 5)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_id_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation_summary') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id, query_string={"verbose": "true"})
        self.assertTrue(len(response.items()) >= len(mock_business.items()))

    def test_get_business_by_ref_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['sampleUnitRef'])
        self.assertEqual(len(response.items()), 5)
        self.assertEqual(response.get('sampleUnitRef'), mock_business['sampleUnitRef'])
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_ref_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['sampleUnitRef'], query_string={"verbose": "true"})
        for x in mock_business:
            self.assertTrue(x in response)

    def test_get_party_by_id_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_id_returns_correct_representation') \
            .as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        response = self.get_party_by_id('B', party_id_b)
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_ref_returns_correct_representation') \
            .as_party()
        self.post_to_parties(mock_party_b, 200)
        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness() \
            .attributes(source='test_existing_business_can_be_updated', version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['version'], 2)

    def test_existing_party_can_be_updated(self):
        mock_party = MockBusiness() \
            .attributes(source='test_existing_party_can_be_updated', version=1)

        response_1 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_party.attributes(version=2)
        response_2 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_post_businesses_with_no_body_returns_400(self):
        self.post_to_businesses(None, 400)

    def test_post_party_with_no_body_returns_400(self):
        self.post_to_parties(None, 400)

    def test_post_party_with_bad_schema_returns_400(self):
        self.post_to_parties({'bad': 'schema'}, 400)

    def test_post_businesses_with_bad_schema_returns_400(self):
        self.post_to_businesses({'bad': 'schema'}, 400)

    def test_get_business_with_invalid_id(self):
        self.get_business_by_id('123', 400)

    def test_get_nonexistent_business_by_id(self):
        party_id = uuid.uuid4()
        self.get_business_by_id(party_id, 404)

    def test_get_nonexistent_business_by_ref(self):
        self.get_business_by_ref('123', 404)

    def test_post_invalid_party(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()
        del mock_party['sampleUnitRef']
        self.post_to_parties(mock_party, 400)

    def test_get_party_with_invalid_unit_type(self):
        self.get_party_by_id('XX', '123', 400)
        self.get_party_by_ref('XX', '123', 400)

    def test_get_party_with_nonexistent_ref(self):
        self.get_party_by_ref('B', '123', 404)




if __name__ == '__main__':
    import unittest

    unittest.main()
