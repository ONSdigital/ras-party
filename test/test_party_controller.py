import uuid
from unittest.mock import MagicMock, patch

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from ras_common_utils.ras_error.ras_error import RasError
from ras_party.controllers import account_controller
from ras_party.models.models import RespondentStatus, Respondent
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.verification import generate_email_token
from test.mocks import MockBusiness, MockRespondent, MockRequests, MockResponse
from test.party_client import PartyTestClient, businesses, respondents, business_respondent_associations, enrolments


class TestParties(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

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
        self.assertEqual(len(response.items()), 5)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_id_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation_summary') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id, query_string={"verbose": "true"})
        self.assertTrue(len(response.items()) >= len(mock_business.items()))

    def test_get_business_by_ref_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['sampleUnitRef'])
        self.assertEqual(len(response.items()), 5)
        self.assertEqual(response.get('sampleUnitRef'), mock_business['sampleUnitRef'])
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_ref_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['sampleUnitRef'], query_string={"verbose": "true"})

        del mock_business['sampleSummaryId']
        for x in mock_business:
            self.assertIn(x, response)

    def test_post_valid_respondent_adds_to_db(self):
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

    def test_get_respondent_by_id_returns_correct_representation(self):
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

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_ref_returns_correct_representation') \
            .as_party()
        self.post_to_parties(mock_party_b, 200)
        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness() \
            .attributes(source='test_existing_business_can_be_updated', version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['version'], 2)

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

    def test_post_respondent_with_inactive_iac(self):
        # Given the IAC code is inactive
        def mock_get_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.get = mock_get_iac
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        # Then status code 400 is returned
        self.post_to_respondents(mock_respondent, 400)

    def test_post_respondent_requests_the_iac_details(self):
        # Given there is a business (related to the IAC code case context)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # When a new respondent is posted
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)
        # Then the case service is called with the supplied IAC code
        self.mock_requests.get.assert_called_once_with('http://mockhost:1111/cases/iac/fb747cq725lj')

    def test_put_respondent_email_returns_400_when_no_email(self):
        self.put_email_to_respondents({}, 400)

    def test_put_respondent_email_changes_email(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)
        self.assertNotEqual("test@test.test", mock_respondent['emailAddress'])
        put_data = {
            "email_address": mock_respondent['emailAddress'],
            "new_email_address": "test@test.test"
        }
        self.put_email_to_respondents(put_data, 200)
        respondent = respondents()[0]
        self.assertEqual("test@test.test", respondent.email_address)

    def test_put_respondent_email_calls_the_notify_service(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)

        self.assertTrue(mock_notify.call_count == 0)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)
        self.assertEqual(mock_notify.verify_email.call_count, 1)
        put_data = {
            "email_address": mock_respondent['emailAddress'],
            "new_email_address": "test@test.test"
        }
        self.put_email_to_respondents(put_data, 200)
        self.assertEqual(mock_notify.verify_email.call_count, 2)

    def test_post_respondent_creates_the_business_respondent_association(self):
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

    def test_post_respondent_creates_the_enrolment(self):
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

    def test_post_respondent_calls_the_notify_service(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        # And an associated respondent
        mock_respondent = MockRespondent().attributes().as_respondent()
        # When a new respondent is posted
        self.post_to_respondents(mock_respondent, 200)
        # Then the (mock) notify service is called
        self.assertTrue(mock_notify.verify_email.called)
        self.assertTrue(mock_notify.verify_email.call_count == 1)

    def test_email_verification_activates_a_respondent(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business and an associated respondent
        self.populate_with_business_and_respondent()

        # And the respondent state is CREATED
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)
        # When the email is verified
        # TODO: this is an awful way of discovering the token, needs to be cleaned-up:
        frontstage_url = mock_notify.verify_email.call_args[0][1]['ACCOUNT_VERIFICATION_URL']
        token = frontstage_url.split('/')[-1]
        self.put_email_verification(token, 200)
        # Then the respondent state is ACTIVE
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.ACTIVE)

    def test_email_verification_url_is_from_config_yml_file(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business and an associated respondent
        self.populate_with_business_and_respondent()

        # And the respondent state is CREATED
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)

        expected_url = 'http://dummy.ons.gov.uk/register/activate-account/'

        # When the email is verified get the email URL from the argument list in the '_send_message_to_gov_uk_notify'
        # method then check the URL is the same as the value configured in the config file
        frontstage_url = mock_notify.verify_email.call_args[0][1]['ACCOUNT_VERIFICATION_URL']
        self.assertIn(expected_url, frontstage_url)

    def test_email_verification_twice_produces_a_200(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business and an associated respondent
        self.populate_with_business_and_respondent()

        # When the email is verified twice
        frontstage_url = mock_notify.verify_email.call_args[0][1]['ACCOUNT_VERIFICATION_URL']
        token = frontstage_url.split('/')[-1]

        self.put_email_verification(token, 200)
        # Then the response is a 200
        self.put_email_verification(token, 200)

    def test_email_verification_unknown_token_produces_a_404(self, *_):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)

        # When an unknown email token exists
        secret_key = "aardvark"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps("brucie@tv.com", salt='bulbous')
        # Then the response is a 404
        self.put_email_verification(token, 404)

    def test_post_respondent_with_no_body_returns_400(self):
        self.post_to_respondents(None, 400)

    def test_post_business_with_no_body_returns_400(self):
        self.post_to_businesses(None, 400)

    def test_post_party_with_no_body_returns_400(self):
        self.post_to_parties(None, 400)

    def test_get_business_with_invalid_id(self):
        self.get_business_by_id('123', 400)

    def test_get_nonexistent_business_by_id(self):
        party_id = uuid.uuid4()
        self.get_business_by_id(party_id, 404)

    def test_get_nonexistent_business_by_ref(self):
        self.get_business_by_ref('123', 404)

    def test_post_invalid_party(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()
        del mock_party['sampleUnitRef']
        self.post_to_parties(mock_party, 400)

    def test_get_party_with_invalid_unit_type(self):
        self.get_party_by_id('XX', '123', 400)
        self.get_party_by_ref('XX', '123', 400)

    def test_get_party_with_nonexistent_ref(self):
        self.get_party_by_ref('B', '123', 404)

    def test_get_respondent_with_invalid_id(self):
        self.get_respondent_by_id('123', 400)

    def test_resend_verification_email(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)

        # Given there is a business and respondent
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        mock_respondent = MockRespondent().attributes().as_respondent()
        resp = self.post_to_respondents(mock_respondent, 200)

        # When the resend verification end point is hit
        self.resend_verification_email(resp['id'], 200)

    def test_resend_verification_email_party_id_not_found(self):
        # Given the party_id sent doesn't exist
        # When the resend verification end point is hit
        response = self.resend_verification_email('3b136c4b-7a14-4904-9e01-13364dd7b972', 404)

        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertIn(account_controller.NO_RESPONDENT_FOR_PARTY_ID, response['errors'])

    def test_resend_verification_email_party_id_malformed(self):
        self.resend_verification_email('malformed', 500)

    def test_request_password_change_calls_notify_gateway(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business and a respondent
        self.populate_with_business_and_respondent()

        # when the request password end point is hit
        self.request_password_change(email='a@z.com')

        # then a notification message is sent to the notify gateway
        self.assertTrue(mock_notify.verify_email.called)
        self.assertEqual(mock_notify.request_password_change.call_count, 1)

    def test_change_password_with_incorrect_token(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        # Given there is a business and a respondent
        self.populate_with_business_and_respondent()

        # when the password is changed with an incorrect token
        token = "fake_token"
        payload = {
            "new_password": "password",
            "token": token
        }

        # it produces a 404
        self.change_password(token, payload, expected_status=404)

    def test_change_respondent_with_valid_token(self):
        # Given a valid token
        token = self.generate_valid_token()
        payload = {
            "new_password": "password",
            "token": token
        }
        # When the password is
        self.change_password(token, payload, expected_status=200)

    def test_verify_token_with_bad_token(self):
        # given a bad token
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps("brucie@tv.com", salt='bulbous')

        # when the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_valid_token(self):
        # given a valid token
        token = self.generate_valid_token()

        # the verify end point verifies the token
        self.verify_token(token, expected_status=200)

    def populate_with_business_and_respondent(self):
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)

    def generate_valid_token(self):
        # ugly way to generate token taken from previous tests
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        self.populate_with_business_and_respondent()
        frontstage_url = mock_notify.verify_email.call_args[0][1]['ACCOUNT_VERIFICATION_URL']
        token = frontstage_url.split('/')[-1]
        return token

    def test_should_reset_password_when_email_wrong_case(self):
        # Given
        # Create respondent
        respondent = Respondent()
        respondent.email_address = 'john@example.com'
        current_app.db.session.add(respondent)
        current_app.db.session.commit()

        # Mock notification
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)

        # When
        self.request_password_change('John@example.com', expected_status=200)

        # Then
        personalisation = {
            'RESET_PASSWORD_URL': PublicWebsite(current_app.config).reset_password_url(respondent.email_address),
            'FIRST_NAME': respondent.first_name
        }
        mock_notify.request_password_change.assert_called_once_with('john@example.com', personalisation, 'None')

    @staticmethod
    def test_verify_token_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db:
            # Given
            token = generate_email_token('test@example.com', current_app.config)

            # When
            # pylint: disable=E1120
            # session is injected by decorator
            account_controller.verify_token(token)

            # Then
            query.assert_called_once_with('test@example.com', db.session())

    @staticmethod
    def test_change_respondent_password_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.OauthClient') as client,\
                patch('ras_party.controllers.account_controller.NotifyGateway'):
            # Given
            token = generate_email_token('test@example.com', current_app.config)
            client().update_account().status_code = 201

            # When
            # pylint: disable=E1120
            # session is injected by decorator
            account_controller.change_respondent_password(token, {'new_password': 'abc'})

            # Then
            query.assert_called_once_with('test@example.com', db.session())

    @staticmethod
    def test_request_password_change_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.NotifyGateway'),\
                patch('ras_party.controllers.account_controller.PublicWebsite'):
            # Given
            payload = {'email_address': 'test@example.com'}

            # When
            # pylint: disable=E1120
            # session is injected by decorator
            account_controller.request_password_change(payload)

            # Then
            query.assert_called_once_with('test@example.com', db.session())

    def test_post_respondent_uses_case_insensitive_email_query(self):
        with patch('ras_party.controllers.queries.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.NotifyGateway'),\
                patch('ras_party.controllers.account_controller.Requests'):
            # Given
            payload = {
                'emailAddress': 'test@example.com',
                'firstName': 'Joe',
                'lastName': 'bloggs',
                'password': 'secure',
                'telephone': '111',
                'enrolmentCode': 'abc'
            }
            query('test@example.com', db.session()).return_value = None

            # When
            # pylint: disable=E1120
            # session is injected by decorator
            with self.assertRaises(RasError):
                account_controller.post_respondent(payload)

            # Then
            query.assert_called_once_with('test@example.com', db.session())

    @staticmethod
    def test_put_email_verification_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db:
            # Given
            token = generate_email_token('test@example.com', current_app.config)

            # When
            # pylint: disable=E1120
            # session is injected by decorator
            account_controller.put_email_verification(token)

            # Then
            query.assert_called_once_with('test@example.com', db.session())


if __name__ == '__main__':
    import unittest

    unittest.main()
