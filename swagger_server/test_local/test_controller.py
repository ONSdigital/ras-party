# coding: utf-8

from __future__ import absolute_import

from flask import json

from swagger_server.configuration import ons_env
from swagger_server.controllers_local import validate
from swagger_server.models_local.model import Business, Party, Respondent, BusinessRespondent
from swagger_server.test_local import BaseTestCase
from swagger_server.test_local.mocks import MockParty, MockBusiness, MockRespondent

db = ons_env

API_VERSION = '1.0.4'


def businesses():
    return db.session.query(Business).all()


def parties():
    return db.session.query(Party).all()


def respondents():
    return db.session.query(Respondent).all()


def business_respondent_associations():
    return db.session.query(BusinessRespondent).all()


''' TODO:
/parties response should include respondents (if they exist)
'''


class TestParties(BaseTestCase):
    def post_to_parties(self, payload, expected_status):
        response = self.client.open('/party-api/{}/parties'.format(API_VERSION),
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_party_by_ref(self, party_type, ref, expected_status=200):
        response = self.client.open('/party-api/{}/parties/type/{}/ref/{}'.format(API_VERSION, party_type, ref),
                                    method='GET')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_party_by_id(self, party_type, id, expected_status=200):
        response = self.client.open('/party-api/{}/parties/type/{}/id/{}'.format(API_VERSION, party_type, id),
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
        mock_business = MockBusiness().attributes(source='test_post_existing_business_updates_db').build()
        self.post_to_parties(mock_business, 200)

        mock_business['attributes'] = {'version': '2'}

        self.post_to_parties(mock_business, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

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

        result = self.get_party_by_ref('B', mock_business['reference'])
        self.assertDictEqual(result, mock_business)

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

        result = self.get_party_by_id('B', party_id)
        self.assertDictEqual(result, mock_business)

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

    def test_post_party_with_missing_party_id_is_rejected(self):
        mock_business = MockBusiness()\
            .attributes(source='test_post_party_with_missing_party_id_is_rejected')\
            .build()
        del mock_business['id']

        response = self.post_to_parties(mock_business, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.Exists.ERROR_MESSAGE.format('id')
        self.assertIn(expected_error, response['errors'])

    def test_post_party_with_missing_reference_is_rejected(self):
        mock_business = MockBusiness() \
            .attributes(source='test_post_party_with_missing_reference_is_rejected') \
            .build()
        del mock_business['reference']

        response = self.post_to_parties(mock_business, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 1)
        expected_error = validate.Exists.ERROR_MESSAGE.format('reference')
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
        del mock_respondent['first_name']
        del mock_respondent['last_name']
        del mock_respondent['telephone']
        del mock_respondent['email_address']

        response = self.post_to_parties(mock_respondent, 400)

        self.assertIn('errors', response)
        self.assertEqual(len(response['errors']), 4)
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('email_address'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('first_name'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('last_name'), response['errors'])
        self.assertIn(validate.Exists.ERROR_MESSAGE.format('telephone'), response['errors'])

    ''' TODO:
    Post business with associations, party uuid doesn't exist
    Post business with association already exists -> should this do an update?
    business-respondent effective dates
    paging parameters
    '''


if __name__ == '__main__':
    import unittest

    unittest.main()
