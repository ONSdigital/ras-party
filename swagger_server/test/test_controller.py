# coding: utf-8

from __future__ import absolute_import

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
        response = self.client.open('/party-api/1.0.0/parties',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))

    def get_party_by_ref(self, party_type, ref):
        query_string = [('sampleUnitType', party_type)]
        response = self.client.open('/party-api/1.0.0/parties/ref/{}'.format(ref),
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))
        return json.loads(response.data)

    def test_post_valid_party_adds_to_db(self):
        mock_party = {
            'attributes': {'source': 'test_post_valid_party_adds_to_db'},
            'id': '65d8c6ed-ab01-4a17-a329-46a1903a2df7',  # -> party_id
            'reference': '49900001234',  # -> ru_ref
            'sampleUnitType': 'B'
        }

        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_existing_party_updates_db(self):
        mock_party = {
            'attributes': {'source': 'test_post_existing_party_updates_db', 'version': '1'},
            'id': '65d8c6ed-ab01-4a17-a329-46a1903a2df7',  # -> party_id
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
            'id': '65d8c6ed-ab01-4a17-a329-46a1903a2df7',  # -> party_id
            'reference': '49900001234'
        }
        self.post_to_parties(mock_party, 400)

        self.assertEqual(len(businesses()), 0)
        self.assertEqual(len(parties()), 0)

    def test_post_party_persists_attributes(self):
        mock_party = {
            'attributes': {'source': 'test_post_party_persists_attributes'},
            'id': '65d8c6ed-ab01-4a17-a329-46a1903a2df7',  # -> party_id
            'reference': '49900001234',
            'sampleUnitType': 'B'
        }
        self.post_to_parties(mock_party, 200)

        business = businesses()[0]
        self.assertDictEqual(business.attributes, {'source': 'test_post_party_persists_attributes'})

    def test_get_party_by_ru_ref_returns_corresponding_business(self):
        mock_party = {
            'attributes': {'source': 'test_post_party_persists_attributes'},
            'id': '65d8c6ed-ab01-4a17-a329-46a1903a2df7',  # -> party_id
            'reference': '49900001234',
            'sampleUnitType': 'B'
        }
        self.post_to_parties(mock_party, 200)

        result = self.get_party_by_ref('B', '49900001234')
        self.assertDictEqual(result, mock_party)

    def test_get_business_party_by_id_returns_corresponding_business(self):
        pass

    def test_get_respondent_party_by_id_returns_corresponding_respondent(self):
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
