# coding: utf-8

from __future__ import absolute_import

from flask import json

from swagger_server.configuration import ons_env
from swagger_server.controllers_local import validate
from swagger_server.models_local.model import Business, Party, Respondent, BusinessRespondent
from swagger_server.test_local import BaseTestCase
from swagger_server.test_local.mocks import MockParty, MockBusiness, MockRespondent

db = ons_env


def businesses():
    return db.session.query(Business).all()


def parties():
    return db.session.query(Party).all()


def respondents():
    return db.session.query(Respondent).all()


def business_respondent_associations():
    return db.session.query(BusinessRespondent).all()


class TestParties(BaseTestCase):
    def post_to_parties(self, payload, expected_status):
        response = self.client.open('/party-api/v1/parties',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_party_by_ref(self, party_type, ref, expected_status=200):
        response = self.client.open('/party-api/v1/parties/type/{}/ref/{}'.format(party_type, ref),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_party_by_id(self, party_type, id, expected_status=200):
        response = self.client.open('/party-api/v1/parties/type/{}/id/{}'.format(party_type, id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_business_by_id(self, id, expected_status=200):
        response = self.client.open('/party-api/v1/businesses/id/{}'.format(id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_business_by_ref(self, ref, expected_status=200):
        response = self.client.open('/party-api/v1/businesses/ref/{}'.format(ref),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_respondent_by_id(self, id, expected_status=200):
        response = self.client.open('/party-api/v1/respondents/id/{}'.format(id),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().attributes(source='test_post_valid_business_adds_to_db').build()

        self.post_to_parties(mock_business, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_valid_respondent_adds_to_db(self):
        mock_respondent = MockRespondent()\
            .build()

        self.post_to_parties(mock_respondent, 200)
        self.assertEqual(len(respondents()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_existing_business_updates_db(self):
        mock_business = MockBusiness().attributes(source='test_post_existing_business_updates_db', version=1).build()
        self.post_to_parties(mock_business, 200)

        business_id = mock_business['id']

        response_1 = self.get_business_by_id(business_id)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_business['attributes']['version'] = 2
        mock_business['attributes']['employeeCount'] = 100
        self.post_to_parties(mock_business, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

        response_2 = self.get_business_by_id(business_id)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_post_party_without_unit_type_does_not_update_db(self):
        mock_business = MockBusiness().attributes(source='test_post_party_without_unit_type_does_not_update_db').build()
        del mock_business['sampleUnitType']

        num_businesses = len(businesses())
        num_parties = len(parties())

        self.post_to_parties(mock_business, 400)

        self.assertEqual(len(businesses()), num_businesses)
        self.assertEqual(len(parties()), num_parties)

    def test_post_party_persists_attributes(self):
        mock_business = MockBusiness().attributes(source='test_post_party_persists_attributes').build()
        self.post_to_parties(mock_business, 200)

        business = businesses()[0]
        self.assertDictEqual(business.attributes, {'source': 'test_post_party_persists_attributes'})

    def test_get_party_by_ru_ref_returns_corresponding_business(self):
        mock_business = MockBusiness()\
            .attributes(source='test_get_party_by_ru_ref_returns_corresponding_business')\
            .build()
        self.post_to_parties(mock_business, 200)

        actual = self.get_party_by_ref('B', mock_business['businessRef'])
        expected = {
            'id': mock_business['id'],
            'businessRef': mock_business['businessRef'],
            'contactName': "John Doe",
            'employeeCount': 50,
            'enterpriseName': "ABC Limited",
            'facsimile': "+44 1234 567890",
            'fulltimeCount': 35,
            'legalStatus': "Private Limited Company",
            'name': "Bolts and Ratchets Ltd",
            'sampleUnitType': mock_business['sampleUnitType'],
            'sic2003': "2520",
            'sic2007': "2520",
            'telephone': "+44 1234 567890",
            'tradingName': "ABC Trading Ltd",
            'turnover': 350,
            'attributes': {'source': 'test_get_party_by_ru_ref_returns_corresponding_business'}
        }
        self.assertDictEqual(actual, expected)

    def test_get_party_by_id_with_invalid_type_is_error(self):
        self.get_party_by_id('BX', '123', 400)

    def test_get_party_by_ref_with_invalid_type_is_error(self):
        self.get_party_by_ref('BX', '123', 400)

    def test_get_party_by_id_returns_corresponding_business(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_party_by_id_returns_corresponding_business') \
            .build()

        party_id = mock_business['id']

        self.post_to_parties(mock_business, 200)

        actual = self.get_party_by_id('B', party_id)
        expected = {
            'id': mock_business['id'],
            'businessRef': mock_business['businessRef'],
            'contactName': "John Doe",
            'employeeCount': 50,
            'enterpriseName': "ABC Limited",
            'facsimile': "+44 1234 567890",
            'fulltimeCount': 35,
            'legalStatus': "Private Limited Company",
            'name': "Bolts and Ratchets Ltd",
            'sampleUnitType': mock_business['sampleUnitType'],
            'sic2003': "2520",
            'sic2007': "2520",
            'telephone': "+44 1234 567890",
            'tradingName': "ABC Trading Ltd",
            'turnover': 350,
            'attributes': {'source': 'test_get_party_by_id_returns_corresponding_business'}
        }
        self.assertDictEqual(actual, expected)

    def test_get_party_by_id_returns_corresponding_respondent(self):
        mock_respondent = MockRespondent().build()

        party_id = mock_respondent['id']

        self.post_to_parties(mock_respondent, 200)
        result = self.get_party_by_id('BI', party_id)
        self.assertDictEqual(result, mock_respondent)

    def test_adding_business_with_associations_is_persisted(self):
        mock_respondent = MockRespondent().properties().build()
        respondent_association = {
            'sampleUnitType': mock_respondent['sampleUnitType'],
            'id': mock_respondent['id']
        }
        mock_business = MockBusiness()\
            .properties(associations=[respondent_association])\
            .attributes(source='test_post_valid_business_adds_to_db')\
            .build()

        self.post_to_parties(mock_respondent, 200)
        self.post_to_parties(mock_business, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(respondents()), 1)
        self.assertEqual(len(parties()), 2)
        self.assertEqual(len(business_respondent_associations()), 1)

    def test_retrieve_business_with_associations(self):
        mock_respondent_1 = MockRespondent().build()
        respondent_association_1 = {
            'sampleUnitType': mock_respondent_1['sampleUnitType'],
            'id': mock_respondent_1['id']
        }
        mock_respondent_2 = MockRespondent().build()
        respondent_association_2 = {
            'sampleUnitType': mock_respondent_2['sampleUnitType'],
            'id': mock_respondent_2['id']
        }
        mock_business = MockBusiness()\
            .properties(associations=[respondent_association_1, respondent_association_2])\
            .attributes(source='test_post_valid_business_adds_to_db')\
            .build()

        self.post_to_parties(mock_respondent_1, 200)
        self.post_to_parties(mock_respondent_2, 200)
        self.post_to_parties(mock_business, 200)

        party_id = mock_business['id']

        result = self.get_party_by_id('B', party_id)

        self.assertIn('associations', result)

        associations = result['associations']
        self.assertEqual(len(associations), 2)

        ids = [a['id'] for a in associations]

        self.assertIn(mock_respondent_1['id'], ids)
        self.assertIn(mock_respondent_2['id'], ids)

    def test_post_party_with_invalid_party_id_is_rejected(self):
        mock_business = MockBusiness()\
            .properties(id='123')\
            .attributes(source='test_post_party_with_invalid_party_id_is_rejected')\
            .build()

        response = self.post_to_parties(mock_business, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.IsUuid.ERROR_MESSAGE.format('123', 'id')
        self.assertIn(expected_error, response['errors'])

    def test_post_party_with_missing_party_id_creates_new_id(self):
        mock_business = MockBusiness()\
            .attributes(source='test_post_party_with_missing_party_id_is_rejected')\
            .build()
        del mock_business['id']

        response = self.post_to_parties(mock_business, 200)

        self.assertIn('id', response)

    def test_post_party_with_missing_reference_is_rejected(self):
        mock_business = MockBusiness() \
            .attributes(source='test_post_party_with_missing_reference_is_rejected') \
            .build()
        del mock_business['businessRef']

        response = self.post_to_parties(mock_business, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.Exists.ERROR_MESSAGE.format('businessRef')
        self.assertIn(expected_error, response['errors'])

    def test_post_party_with_unknown_unit_type_is_rejected(self):
        mock_business = MockParty('BX') \
            .build()

        response = self.post_to_parties(mock_business, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.IsIn.ERROR_MESSAGE.format('BX', 'sampleUnitType', ('B', 'BI'))
        self.assertIn(expected_error, response['errors'])

    def test_post_respondent_with_missing_details_is_rejected(self):
        mock_respondent = MockRespondent().build()
        del mock_respondent['firstName']
        del mock_respondent['lastName']
        del mock_respondent['telephone']
        del mock_respondent['emailAddress']

        response = self.post_to_parties(mock_respondent, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 4)
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('emailAddress'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('firstName'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('lastName'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('telephone'), response['errors'])

    def test_post_existing_respondent_updates_details(self):
        mock_respondent = MockRespondent().build()

        self.post_to_parties(mock_respondent, 200)
        persisted = respondents()
        self.assertEqual(len(persisted), 1)
        self.assertEqual(len(parties()), 1)

        self.assertEqual(persisted[0].first_name, 'A')

        mock_respondent['firstName'] = 'Z'
        self.post_to_parties(mock_respondent, 200)
        persisted = respondents()
        self.assertEqual(len(persisted), 1)
        self.assertEqual(len(parties()), 1)

        self.assertEqual(persisted[0].first_name, 'Z')

    def test_get_business_with_invalid_id_is_rejected(self):

        response = self.get_business_by_id('123', 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.IsUuid.ERROR_MESSAGE.format('123', 'id')
        self.assertIn(expected_error, response['errors'])

    def test_get_respondent_with_invalid_id_is_rejected(self):

        response = self.get_respondent_by_id('123', 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.IsUuid.ERROR_MESSAGE.format('123', 'id')
        self.assertIn(expected_error, response['errors'])

    def test_get_non_existing_business_is_404(self):
        self.get_business_by_id('31317c23-763d-46a9-b4e5-c37ff5b4fbe7', 404)

        self.get_business_by_ref('123', 404)

    def test_get_non_existing_respondent_is_404(self):
        self.get_respondent_by_id('31317c23-763d-46a9-b4e5-c37ff5b4fbe7', 404)

    ''' TODO:
    Post business with associations, party uuid doesn't exist
    Post business with association already exists -> should this do an update?
    business-respondent effective dates
    paging parameters
    '''


if __name__ == '__main__':
    import unittest

    unittest.main()
