# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.residence import Residence
from swagger_server.models.vnd_collectionjson import VndCollectionjson
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestFutureController(BaseTestCase):
    """ FutureController integration test stubs """

    def test_get_residence_by_id(self):
        """
        Test case for get_residence_by_id

        Get a Residence by its Party ID
        """
        response = self.client.open('/party-api/1.0.0/residences/id/{id}'.format(id='id_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_residence_by_uprn(self):
        """
        Test case for get_residence_by_uprn

        Get a Residence by its unique property reference
        """
        response = self.client.open('/party-api/1.0.0/residences/uprn/{uprn}'.format(uprn='uprn_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_residences_get(self):
        """
        Test case for residences_get

        searches Residences
        """
        query_string = [('searchString', 'searchString_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/residences',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_residences_id_id_options(self):
        """
        Test case for residences_id_id_options

        View the available representations for a given Residence
        """
        response = self.client.open('/party-api/1.0.0/residences/id/{id}'.format(id='id_example'),
                                    method='OPTIONS')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_residences_id_id_put(self):
        """
        Test case for residences_id_id_put

        Update the representation for an existing Residence
        """
        headers = [('ETag', 'ETag_example')]
        data = dict(binaryparty=(BytesIO(b'some file data'), 'file.txt'))
        response = self.client.open('/party-api/1.0.0/residences/id/{id}'.format(id='id_example'),
                                    method='PUT',
                                    headers=headers,
                                    data=data,
                                    content_type='multipart/form-data')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_residences_post(self):
        """
        Test case for residences_post

        adds a reporting unit of type Residence
        """
        party = Residence()
        response = self.client.open('/party-api/1.0.0/residences',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.party+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
