# coding: utf-8

from __future__ import absolute_import

import uuid

from flask import json

from swagger_server.models.party import Party
from swagger_server.test_local import BaseTestCase


class TestParties(BaseTestCase):
    """ BackstageController integration test stubs """

    def test_post_valid_party_returns_200(self):
        mock_party = {
            "attributes": {},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",   # -> party_id
            "reference": "49900001234",   # -> ru_ref
            "sampleUnitType": "B"
        }
        response = self.client.open('/party-api/1.0.0/parties',
                                    method='POST',
                                    data=json.dumps(mock_party),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, 201, "Response body is : " + response.data.decode('utf-8'))

    def test_post_party_without_unit_type_returns_400(self):
        mock_party = {
            "attributes": {},
            "id": "65d8c6ed-ab01-4a17-a329-46a1903a2df7",   # -> party_id
            "reference": "49900001234"
        }
        response = self.client.open('/party-api/1.0.0/parties',
                                    method='POST',
                                    data=json.dumps(mock_party),
                                    content_type='application/vnd.ons.business+json')
        self.assertStatus(response, 400, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
