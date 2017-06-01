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
    """ BackstageController integration test stubs """

    def post_to_parties(self, payload, expected_status):
        response = self.client.open('/party-api/1.0.0/parties',
                                    method='POST',
                                    data=json.dumps(payload),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, expected_status, "Response body is : " + response.data.decode('utf-8'))

    def test_post_valid_party_adds_to_db(self):
        mock_party = {
            "attributes": {'source': 'test_post_valid_party_returns_201'},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",  # -> party_id
            "reference": "49900001234",  # -> ru_ref
            "sampleUnitType": "B"
        }

        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_existing_party_updates_db(self):
        mock_party = {
            "attributes": {'source': 'test_post_existing_party_returns_201'},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",  # -> party_id
            "reference": "49900001234",  # -> ru_ref
            "sampleUnitType": "B"
        }
        self.post_to_parties(mock_party, 200)

        mock_party['reference'] = '123'

        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(len(parties()), 1)

    def test_post_party_without_unit_type_does_not_update_db(self):
        mock_party = {
            "attributes": {'source': 'test_post_party_without_unit_type_returns_400'},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",  # -> party_id
            "reference": "49900001234"
        }
        self.post_to_parties(mock_party, 400)

        self.assertEqual(len(businesses()), 0)
        self.assertEqual(len(parties()), 0)

    def test_post_party_persists_attributes(self):
        mock_party = {
            "attributes": {'source': 'test_post_party_persists_attributes'},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",  # -> party_id
            "reference": "49900001234",
            "sampleUnitType": "B"
        }
        self.post_to_parties(mock_party, 200)

        business = businesses()[0]
        self.assertDictEqual(business.attributes, {'source': 'test_post_party_persists_attributes'})


if __name__ == '__main__':
    import unittest

    unittest.main()
