# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.business import Business
from swagger_server.models.enrolment_code import EnrolmentCode
from swagger_server.models.enrolment_invitation import EnrolmentInvitation
from swagger_server.models.error import Error
from swagger_server.models.respondent import Respondent
from swagger_server.models.vnd_collectionjson import VndCollectionjson
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestFrontstageController(BaseTestCase):
    """ FrontstageController integration test stubs """

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

    def test_businesses_id_id_options(self):
        """
        Test case for businesses_id_id_options

        View the available representations for a given Business
        """
        response = self.client.open('/party-api/1.0.0/businesses/id/{id}'.format(id='id_example'),
                                    method='OPTIONS')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_enrolment_codes_post(self):
        """
        Test case for enrolment_codes_post

        redeems an Enrolment Code
        """
        party = EnrolmentCode()
        response = self.client.open('/party-api/1.0.0/enrolment-codes',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.enrolment-code+json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_enrolment_invitations_post(self):
        """
        Test case for enrolment_invitations_post

        stores an invitation to Enrol another Respondent to a Survey
        """
        party = EnrolmentInvitation()
        response = self.client.open('/party-api/1.0.0/enrolment-invitations',
                                    method='POST',
                                    data=json.dumps(party),
                                    content_type='application/vnd.ons.enrolment-invitation+json')
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
