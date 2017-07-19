from __future__ import absolute_import

from unittest.mock import patch

from itsdangerous import URLSafeTimedSerializer

from ras_party.models.models import RespondentStatus
from test.mocks import MockBusiness, MockRespondent, MockRequests
from test.party_client import PartyTestClient, businesses, respondents, business_respondent_associations, enrolments


class TestParties(PartyTestClient):
    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

    def test_get_business_by_id_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id)
        self.assertTrue(response.items() >= mock_business.items())

    def test_get_business_by_ref_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['businessRef'])
        self.assertTrue(response.items() >= mock_business.items())

    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_post_valid_respondent_adds_to_db(self, _):
        # Given the database contains no respondents
        self.assertEqual(len(respondents()), 0)
        # And there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)
        # Then the database contains a respondent
        self.assertEqual(len(respondents()), 1)

    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_get_respondent_by_id_returns_correct_representation(self, _):
        # Given there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        resp = self.post_to_respondents(mock_respondent, 200)
        party_id = resp['id']
        # And we get the new respondent
        response = self.get_respondent_by_id(party_id)

        # Not expecting the enrolmentCode to be returned as part of the respondent
        del mock_respondent['enrolmentCode']
        # Then the response matches the posted respondent
        self.assertTrue('id' in response)
        self.assertEqual(response['emailAddress'], mock_respondent['emailAddress'])
        self.assertEqual(response['firstName'], mock_respondent['firstName'])
        self.assertEqual(response['lastName'], mock_respondent['lastName'])
        self.assertEqual(response['sampleUnitType'], mock_respondent['sampleUnitType'])
        self.assertEqual(response['telephone'], mock_respondent['telephone'])

    def test_post_valid_party_adds_to_db(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()

        self.post_to_parties(mock_party, 200)
        self.assertEqual(len(businesses()), 1)

        mock_party = MockRespondent().attributes().as_respondent()

        self.post_to_parties(mock_party, 400)
        self.assertEqual(len(businesses()), 1)

    def test_get_party_by_id_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_id_returns_correct_representation') \
            .as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        response = self.get_party_by_id('B', party_id_b)
        self.assertTrue(response.items() >= mock_party_b.items())

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_ref_returns_correct_representation') \
            .as_party()
        self.post_to_parties(mock_party_b, 200)

        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])
        self.assertTrue(response.items() >= mock_party_b.items())

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness() \
            .attributes(source='test_existing_business_can_be_updated', version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_existing_respondent_can_be_updated(self):
        # TODO: clarify the PK on which an update would be done
        # FIXME: this functionality is likely to be broken following enrolment updates
        pass

    def test_existing_party_can_be_updated(self):
        mock_party = MockBusiness() \
            .attributes(source='test_existing_respondent_can_be_updated', version=1)

        response_1 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_party.attributes(version=2)
        response_2 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    # TODO: maybe remove the interaction test once things are working?
    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_post_respondent_requests_the_iac_details(self, mock):
        # Given there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)
        # Then the case service is called with the supplied IAC code
        mock.get.assert_called_once_with('http://mockhost:1111/cases/iac/fb747cq725lj')

    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_post_respondent_creates_the_business_respondent_association(self, _):
        # Given the database contains no associations
        self.assertEqual(len(business_respondent_associations()), 0)
        # And there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        created_respondent = self.post_to_respondents(mock_respondent, 200)
        # Then the database contains an association
        self.assertEqual(len(business_respondent_associations()), 1)
        # And the association is between the given business and respondent
        assoc = business_respondent_associations()[0]
        business_id = assoc.business_id
        respondent_id = assoc.respondent.party_uuid
        self.assertEqual(str(business_id), '3b136c4b-7a14-4904-9e01-13364dd7b972')
        self.assertEqual(str(respondent_id), created_respondent['id'])

    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_post_respondent_creates_the_enrolment(self, _):
        # Given the database contains no enrolments
        self.assertEqual(len(enrolments()), 0)
        # And there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        created_respondent = self.post_to_respondents(mock_respondent, 200)
        # Then the database contains an association
        self.assertEqual(len(enrolments()), 1)
        enrolment = enrolments()[0]
        # And the enrolment contains the survey id given in the survey fixture
        self.assertEqual(str(enrolment.survey_id), 'cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87')
        # And is linked to the created respondent
        self.assertEqual(str(enrolment.business_respondent.respondent.party_uuid),
                         created_respondent['id'])
        # And is linked to the given business
        self.assertEqual(str(enrolment.business_respondent.business.party_uuid),
                         '3b136c4b-7a14-4904-9e01-13364dd7b972')

    @patch('ras_party.controllers.controller.notify')
    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_post_respondent_calls_the_notify_service(self, _, mock_notify):
        # Given there is a business
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # And an associated respondent
        mock_respondent = MockRespondent().attributes().as_respondent()
        # When a new respondent is posted
        self.post_to_respondents(mock_respondent, 200)

        # Then the (mock) notify service is called
        mock_notify.assert_called_once()

    @patch('ras_party.controllers.controller.notify')
    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_email_verification_activates_a_respondent(self, _, mock_notify):
        # Given there is a business
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # And an associated respondent
        mock_respondent = MockRespondent().attributes().as_respondent()
        # And a new respondent (which generates an email verification)
        self.post_to_respondents(mock_respondent, 200)
        # And the respondent state is CREATED
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)

        # When the email is verified
        frontstage_url = mock_notify.call_args[0][0]
        _, token = frontstage_url.split('=')
        self.put_email_verification(token, 200)

        # Then the respondent state is ACTIVE
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.ACTIVE)

    @patch('ras_party.controllers.controller.notify')
    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_email_verification_twice_produces_a_409(self, _, mock_notify):
        # Given there is a business
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # And an associated respondent
        mock_respondent = MockRespondent().attributes().as_respondent()
        # And a new respondent (which generates an email verification)
        self.post_to_respondents(mock_respondent, 200)

        # When the email is verified twice
        frontstage_url = mock_notify.call_args[0][0]
        _, token = frontstage_url.split('=')
        self.put_email_verification(token, 200)
        # Then the response is a 409
        self.put_email_verification(token, 409)

    @patch('ras_party.controllers.controller.notify')
    @patch('ras_party.controllers.controller.requests', new_callable=MockRequests)
    def test_email_verification_unknown_token_produces_a_404(self, *_):
        # When an unknown email token exists
        secret_key = "aardvark"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps("brucie@tv.com", salt='bulbous')
        # Then the response is a 404
        self.put_email_verification(token, 404)


if __name__ == '__main__':
    import unittest

    unittest.main()
