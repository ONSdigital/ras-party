# coding: utf-8

from __future__ import absolute_import

import uuid

from flask import json

from swagger_server.configuration import ons_env
from swagger_server.models.model import Business, Party
from swagger_server.test import BaseTestCase

db = ons_env


def businesses():
    return db.session.query(Business).all()


def parties():
    return db.session.query(Party).all()


class TestParties(BaseTestCase):
    def post_to_parties(self, payload, expected_status):
        response = self.client.open('/party-api/1.0.1/parties',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))

    def get_party_by_ref(self, party_type, ref):
        response = self.client.open('/party-api/1.0.1/parties/type/{}/ref/{}'.format(party_type, ref),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def get_party_by_id(self, party_type, id):
        query_string = ['']

    def test_post_valid_party_adds_to_db(self):
        mock_party = {
            'attributes': {'source': 'test_post_valid_party_adds_to_db'},
            'id': str(uuid.uuid4()),  # -> party_uuid
            'reference': '49900001234',  # -> ru_ref
            'sampleUnitType': 'B'
        }

        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_existing_party_updates_db(self):
        mock_party = {
            'attributes': {'source': 'test_post_existing_party_updates_db', 'version': '1'},
            'id': str(uuid.uuid4()),  # -> party_uuid
            'reference': '49900001234',  # -> ru_ref
            'sampleUnitType': 'B'
        }
        self.post_to_parties(mock_party, 200)

        mock_party['attributes'] = {'version': '2'}

        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_party_without_unit_type_does_not_update_db(self):
        mock_party = {
            'attributes': {'source': 'test_post_party_without_unit_type_does_not_update_db'},
            'id': str(uuid.uuid4()),
            'reference': '49900001234'
        }

        num_businesses = len(businesses())
        num_parties = len(parties())

        self.post_to_parties(mock_party, 400)

        self.assertEqual(len(businesses()), num_businesses)
        self.assertEqual(len(parties()), num_parties)

    def test_post_party_persists_attributes(self):
        mock_party = {
            'attributes': {'source': 'test_post_party_persists_attributes'},
            'id': str(uuid.uuid4()),  # -> party_id
            'reference': '49900001234',
            'sampleUnitType': 'B'
        }
        self.post_to_parties(mock_party, 200)

        business = businesses()[0]
        self.assertDictEqual(business.attributes, {'source': 'test_post_party_persists_attributes'})

    def test_get_party_by_ru_ref_returns_corresponding_business(self):
        mock_party = {
            'attributes': {'source': 'test_post_party_persists_attributes'},
            'id': str(uuid.uuid4()),  # -> party_uuid
            'reference': '49900001234',
            'sampleUnitType': 'B'
        }
        self.post_to_parties(mock_party, 200)

        result = self.get_party_by_ref('B', '49900001234')
        self.assertDictEqual(result, mock_party)

    # def test_get_party_by_id_returns_corresponding_business(self):
    #     party_id = str(uuid.uuid4())
    #     mock_party = {
    #         'attributes': {'source': 'test_post_party_persists_attributes'},
    #         'id': party_id,  # -> party_uuid
    #         'reference': '49900001235',
    #         'sampleUnitType': 'B'
    #     }
    #     self.post_to_parties(mock_party, 200)
    #
    #     result = self.get_party_by_id('B', party_id)
    #     self.assertDictEqual(result, mock_party)

    def test_get_party_by_id_returns_corresponding_respondent(self):
        pass


class TestBusinesses(BaseTestCase):

    def test_get_business_by_id_returns_corresponding_business(self):
        pass


class TestRespondents(BaseTestCase):

    def test_get_respondent_by_id_returns_corresponding_business(self):
        pass


if __name__ == '__main__':
    import unittest

    unittest.main()
