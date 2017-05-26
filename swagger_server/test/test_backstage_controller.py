# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.business import Business
from swagger_server.models.error import Error
from swagger_server.models.party import Party
from swagger_server.models.respondent import Respondent
from swagger_server.models.vnd_collectionjson import VndCollectionjson
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestBackstageController(BaseTestCase):
    """ BackstageController integration test stubs """

    def test_businesses_get(self):
        """
        Test case for businesses_get

        searches Businesses
        """
        query_string = [('searchString', 'searchString_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/businesses',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_businesses_id_id_business_associations_get(self):
        """
        Test case for businesses_id_id_business_associations_get

        Returns the known business associations for a business
        """
        query_string = [('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/businesses/id/{id}/business-associations'.format(id='id_example'),
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_businesses_id_id_options(self):
        """
        Test case for businesses_id_id_options

        View the available representations for a given Business
        """
        response = self.client.open('/party-api/1.0.0/businesses/id/{id}'.format(id='id_example'),
                                    method='OPTIONS')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_businesses_id_id_put(self):
        """
        Test case for businesses_id_id_put

        Update the representation for an existing Business
        """
        headers = [('ETag', 'ETag_example')]
        data = dict(binaryparty=(BytesIO(b'some file data'), 'file.txt'))
        response = self.client.open('/party-api/1.0.0/businesses/id/{id}'.format(id='id_example'),
                                    method='PUT',
                                    headers=headers,
                                    data=data,
                                    content_type='multipart/form-data')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_businesses_post(self):
        """
        Test case for businesses_post

        adds a reporting unit of type Business
        """
        party = Party()
        response = self.client.open('/party-api/1.0.0/businesses',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.business+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_enrolment_codes_get(self):
        """
        Test case for enrolment_codes_get

        searches enrolment codes
        """
        query_string = [('searchString', 'searchString_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/enrolment-codes',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_enrolment_invitations_get(self):
        """
        Test case for enrolment_invitations_get

        searches enrolment invitations
        """
        query_string = [('searchString', 'searchString_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/enrolment-invitations',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_business_by_id(self):
        """
        Test case for get_business_by_id

        Get a Business by its Party ID
        """
        response = self.client.open('/party-api/1.0.0/businesses/id/{id}'.format(id='id_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_business_by_ref(self):
        """
        Test case for get_business_by_ref

        Get a Business by its unique business reference
        """
        response = self.client.open('/party-api/1.0.0/businesses/ref/{ref}'.format(ref='ref_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_party_by_ref(self):
        """
        Test case for get_party_by_ref

        Get a Party by its unique reference (ruref / uprn)
        """
        response = self.client.open('/party-api/1.0.0/parties/ref/{ref}'.format(ref='ref_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_respondent_by_id(self):
        """
        Test case for get_respondent_by_id

        Get a Respondent by its Party ID
        """
        response = self.client.open('/party-api/1.0.0/respondents/id/{id}'.format(id='id_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_parties_post(self):
        """
        Test case for parties_post

        given a sampleUnitType B | H this adds a reporting unit of type Business or Household
        """
        party = Party()
        response = self.client.open('/party-api/1.0.0/parties',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.party+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_respondents_get(self):
        """
        Test case for respondents_get

        searches Respondents
        """
        query_string = [('searchString', 'searchString_example'),
                        ('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/respondents',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_respondents_id_id_business_associations_get(self):
        """
        Test case for respondents_id_id_business_associations_get

        Returns the known business associations for a respondent
        """
        query_string = [('skip', 1),
                        ('limit', 50)]
        response = self.client.open('/party-api/1.0.0/respondents/id/{id}/business-associations'.format(id='id_example'),
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_respondents_id_id_options(self):
        """
        Test case for respondents_id_id_options

        View the available representations for a given Respondent
        """
        response = self.client.open('/party-api/1.0.0/respondents/id/{id}'.format(id='id_example'),
                                    method='OPTIONS')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_respondents_id_id_put(self):
        """
        Test case for respondents_id_id_put

        Update the representation for an existing Respondent.
        """
        headers = [('ETag', 'ETag_example')]
        response = self.client.open('/party-api/1.0.0/respondents/id/{id}'.format(id='id_example'),
                                    method='PUT',
                                    headers=headers,
                                    content_type='application/vnd.ons.respondent+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_respondents_post(self):
        """
        Test case for respondents_post

        adds a Respondent
        """
        party = Respondent()
        response = self.client.open('/party-api/1.0.0/respondents',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.respondent+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
