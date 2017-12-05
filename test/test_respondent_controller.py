import uuid
from unittest.mock import MagicMock, patch

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from ras_common_utils.ras_error.ras_error import RasError
from ras_party.controllers import account_controller
from ras_party.models.models import RespondentStatus, Respondent
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.transactional import transactional
from ras_party.support.verification import generate_email_token
from test.mocks import MockBusiness, MockRespondent, MockRequests, MockResponse
from test.party_client import PartyTestClient, respondents, business_respondent_associations, enrolments


class TestRespondents(PartyTestClient):

    def setUp(self):
        self.assertEqual(len(respondents()), 0)
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests
        self.mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=self.mock_notify)
        self.mock_respondent = MockRespondent().attributes().as_respondent()
        self.respondent = None

    @with_db_session
    def tearDown(self, session):
        if self.respondent:
            session.delete(self.respondent)

    def generate_valid_token_from_email(self, email):
        frontstage_url = PublicWebsite(current_app.config).activate_account_url(email)
        token = frontstage_url.split('/')[-1]
        return token

    @transactional
    @with_db_session
    def add_respondent_to_db_and_oauth(self, party, tran, session):
        translated_party = {
            'party_uuid': party.get('id') or str(uuid.uuid4()),
            'email_address': party['emailAddress'],
            'first_name': party['firstName'],
            'last_name': party['lastName'],
            'telephone': party['telephone'],
            'status': RespondentStatus.CREATED
        }
        self.respondent = Respondent(**translated_party)
        session.add(self.respondent)
        account_controller.register_user(party, tran)
        return self.respondent

    def test_get_respondent_with_invalid_id(self):
        self.get_respondent_by_id('123', 400)

    def test_get_respondent_with_valid_id(self):
        self.get_respondent_by_id(str(uuid.uuid4()), 404)

    def test_get_respondent_by_id_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # And we get the new respondent
        response = self.get_respondent_by_id(respondent.party_uuid)
        # Then the response matches the posted respondent
        self.assertTrue('id' in response)
        self.assertEqual(response['emailAddress'], self.mock_respondent['emailAddress'])
        self.assertEqual(response['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response['telephone'], self.mock_respondent['telephone'])

    def test_get_respondent_with_invalid_email(self):
        self.get_respondent_by_email('123', 404)

    def test_get_respondent_with_valid_email(self):
        self.get_respondent_by_email('test@example.test', 404)

    def test_get_respondent_by_email_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # And we get the new respondent
        response = self.get_respondent_by_email(respondent.email_address)
        # Then the response matches the posted respondent
        self.assertTrue('id' in response)
        self.assertEqual(response['emailAddress'], self.mock_respondent['emailAddress'])
        self.assertEqual(response['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response['telephone'], self.mock_respondent['telephone'])

    def test_resend_verification_email(self):
        # Given there is a respondent
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # When the resend verification end point is hit
        self.resend_verification_email(respondent.party_uuid)

    def test_resend_verification_email_calls_notify_gateway(self):
        # Given there is a respondent
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # When the resend verification end point is hit
        self.resend_verification_email(respondent.party_uuid)
        # Verification email is sent
        self.assertTrue(self.mock_notify.verify_email.called)

    def test_resend_verification_email_responds_with_message(self):
        # Given there is a respondent
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # When the resend verification end point is hit
        response = self.resend_verification_email(respondent.party_uuid)
        # Message is present in response
        self.assertIn(account_controller.EMAIL_VERIFICATION_SENT, response['message'])

    def test_resend_verification_email_party_id_not_found(self):
        # Given the party_id sent doesn't exist
        # When the resend verification end point is hit
        response = self.resend_verification_email('3b136c4b-7a14-4904-9e01-13364dd7b972', 404)
        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertFalse(self.mock_notify.verify_email.called)
        self.assertIn(account_controller.NO_RESPONDENT_FOR_PARTY_ID, response['errors'])

    def test_resend_verification_email_party_id_malformed(self):
        self.resend_verification_email('malformed', 500)

    def test_request_password_change_with_valid_email(self):
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        payload = {'email_address': respondent.email_address}
        self.request_password_change(payload)

    def test_request_password_change_calls_notify_gateway(self):
        # Given there is a respondent
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        # When the request password end point is hit with an existing email address
        payload = {'email_address': respondent.email_address}
        self.request_password_change(payload)
        # Then a notification message is sent to the notify gateway
        personalisation = {
            'RESET_PASSWORD_URL': PublicWebsite(current_app.config).reset_password_url(respondent.email_address),
            'FIRST_NAME': respondent.first_name
        }
        self.mock_notify.request_password_change.assert_called_once_with(
            respondent.email_address,
            personalisation,
            respondent.party_uuid
        )

    def test_request_password_change_with_no_email(self):
        payload = {}
        self.request_password_change(payload, expected_status=400)

    def test_request_password_change_with_empty_email(self):
        payload = {'email_address': ''}
        self.request_password_change(payload, expected_status=404)

    def test_request_password_change_with_other_email(self):
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        payload = {'email_address': 'not-mock@example.test'}
        self.request_password_change(payload, expected_status=404)
        self.assertFalse(self.mock_notify.request_password_change.called)

    def test_request_password_change_with_malformed_email(self):
        payload = {'email_address': 'malformed'}
        self.request_password_change(payload, expected_status=404)

    def test_should_reset_password_when_email_wrong_case(self):
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        payload = {'email_address': respondent.email_address.upper()}
        self.request_password_change(payload)
        personalisation = {
            'RESET_PASSWORD_URL': PublicWebsite(current_app.config).reset_password_url(respondent.email_address),
            'FIRST_NAME': respondent.first_name
        }
        self.mock_notify.request_password_change.assert_called_once_with(
            respondent.email_address,
            personalisation,
            respondent.party_uuid
        )

    @staticmethod
    def test_request_password_change_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.NotifyGateway'),\
                patch('ras_party.controllers.account_controller.PublicWebsite'):
            payload = {'email_address': 'test@example.test'}
            account_controller.request_password_change(payload)
            query.assert_called_once_with('test@example.test', db.session())

    def test_change_password_with_invalid_token(self):
        # When the password is changed with an incorrect token
        token = 'fake_token'
        payload = {
            'new_password': 'password',
            'token': token
        }
        self.change_password(token, payload, expected_status=404)

    def test_change_password_with_no_password(self):
        # When the password is changed with a valid token and no password
        token = self.generate_valid_token_from_email('mock@email.com')
        payload = {
            'token': token
        }
        self.change_password(token, payload, expected_status=400)

    def test_change_password_with_empty_password(self):
        # When the password is changed with a token that does not match respondent
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        token = self.generate_valid_token_from_email('not-mock@email.com')
        payload = {
            'new_password': '',
            'token': token
        }
        self.change_password(token, payload, expected_status=404)

    def test_change_password_with_other_token(self):
        # When the password is changed with a token that does not match respondent
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        token = self.generate_valid_token_from_email('not-mock@email.com')
        payload = {
            'new_password': 'password',
            'token': token
        }
        self.change_password(token, payload, expected_status=404)

    def test_change_password_with_no_respondent(self):
        # When the password is changed with no respondents in db
        token = self.generate_valid_token_from_email(self.mock_respondent['emailAddress'])
        payload = {
            'new_password': 'password',
            'token': token
        }
        self.change_password(token, payload, expected_status=404)

    def test_change_password_with_valid_token(self):
        # Given a valid token from the respondent
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        token = self.generate_valid_token_from_email(respondent.email_address)
        payload = {
            'new_password': 'password',
            'token': token
        }
        # When the password is changed
        self.change_password(token, payload, expected_status=200)
        personalisation = {
            'FIRST_NAME': respondent.first_name
        }
        self.mock_notify.confirm_password_change.assert_called_once_with(
            respondent.email_address,
            personalisation,
            respondent.party_uuid
        )

    @staticmethod
    def test_change_respondent_password_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.OauthClient') as client,\
                patch('ras_party.controllers.account_controller.NotifyGateway'):
            token = generate_email_token('test@example.test', current_app.config)
            client().update_account().status_code = 201
            account_controller.change_respondent_password(token, {'new_password': 'abc'})
            query.assert_called_once_with('test@example.test', db.session())

    def test_verify_token_with_bad_secrets(self):
        # Given a respondent exists with an invalid token
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(respondent.email_address, salt='salt')
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_bad_email(self):
        # Given a respondent in the db but other email
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        secret_key = current_app.config['SECRET_KEY']
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps('not-mock@example.test', salt=current_app.config['EMAIL_TOKEN_SALT'])
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_valid_token(self):
        # Given respondent exists with a valid token
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        secret_key = current_app.config['SECRET_KEY']
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(respondent.email_address, salt=current_app.config['EMAIL_TOKEN_SALT'])
        # Then the verify end point verifies the token
        self.verify_token(token)

    @staticmethod
    def test_verify_token_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db:
            token = generate_email_token('test@example.test', current_app.config)
            account_controller.verify_token(token)
            query.assert_called_once_with('test@example.test', db.session())

    def test_put_respondent_email_returns_400_when_no_email(self):
        self.put_email_to_respondents({}, 400)

    def test_put_respondent_email_returns_400_when_no_new_email(self):
        put_data = {'email_address': self.mock_respondent['emailAddress']}
        self.put_email_to_respondents(put_data, 400)

    def test_put_respondent_email_returns_404_when_no_respondent(self):
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': 'test@example.test',
        }
        self.put_email_to_respondents(put_data, 404)

    def test_put_respondent_email_returns_respondent_same_email(self):
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': self.mock_respondent['emailAddress'],
        }
        response = self.put_email_to_respondents(put_data)
        self.assertTrue(respondents()[0].email_address == response['emailAddress'])

    def test_put_respondent_email_returns_409_existing_email(self):
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        mock_respondent_b = self.mock_respondent.copy()
        mock_respondent_b['emailAddress'] = 'test@example.test'
        self.add_respondent_to_db_and_oauth(mock_respondent_b)

        put_data = {
            'email_address': respondent.email_address,
            'new_email_address': mock_respondent_b['emailAddress'],
        }
        self.put_email_to_respondents(put_data, 409)

    def test_put_respondent_email_new_email(self):
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': 'test@example.test',
        }
        self.put_email_to_respondents(put_data)
        self.assertEqual(respondents()[0].email_address, 'test@example.test')

    def test_put_respondent_email_calls_the_notify_service(self):
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': 'test@example.test'
        }
        self.put_email_to_respondents(put_data)
        personalisation = {
            'ACCOUNT_VERIFICATION_URL': PublicWebsite(current_app.config).activate_account_url('test@example.test'),
        }
        self.mock_notify.verify_email.assert_called_once_with(
            'test@example.test',
            personalisation,
            respondent.party_uuid
        )

    def test_email_verification_activates_a_respondent(self):
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        response = self.put_email_verification(token, 200)
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.ACTIVE)
        self.assertEqual(response['status'], RespondentStatus.ACTIVE.name)

    def test_email_verification_url_is_from_config_yml_file(self):
        account_controller._send_email_verification(0, 'test@example.test')
        expected_url = 'http://dummy.ons.gov.uk/register/activate-account/'
        frontstage_url = self.mock_notify.verify_email.call_args[0][1]['ACCOUNT_VERIFICATION_URL']
        self.assertIn(expected_url, frontstage_url)

    def test_email_verification_twice_produces_a_200(self):
        respondent = self.add_respondent_to_db_and_oauth(self.mock_respondent)
        token = self.generate_valid_token_from_email(respondent.email_address)
        self.put_email_verification(token, 200)
        response = self.put_email_verification(token, 200)
        self.assertEqual(response['status'], RespondentStatus.ACTIVE.name)

    def test_email_verification_bad_token_produces_a_404(self):
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(self.mock_respondent['emailAddress'], salt='salt')
        self.put_email_verification(token, 404)

    def test_email_verification_unknown_email_produces_a_404(self):
        self.add_respondent_to_db_and_oauth(self.mock_respondent)
        token = self.generate_valid_token_from_email('test@example.test')
        self.put_email_verification(token, 404)
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)

    def test_put_email_verification_uses_case_insensitive_email_query(self):
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db:
            token = self.generate_valid_token_from_email('test@example.test')
            account_controller.put_email_verification(token)
            query.assert_called_once_with('test@example.test', db.session())

    def test_post_respondent_with_payload_returns_200(self):
        mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=mock_notify)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = '3b136c4b-7a14-4904-9e01-13364dd7b972'
        self.post_to_businesses(mock_business, 200)
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)

    def test_post_respondent_with_no_payload_returns_400(self):
        self.post_to_respondents(None, 400)

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

    def test_post_respondent_uses_case_insensitive_email_query(self):
        with patch('ras_party.controllers.queries.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db,\
                patch('ras_party.controllers.account_controller.NotifyGateway'),\
                patch('ras_party.controllers.account_controller.Requests'):
            payload = {
                'emailAddress': 'test@example.test',
                'firstName': 'Joe',
                'lastName': 'bloggs',
                'password': 'secure',
                'telephone': '111',
                'enrolmentCode': 'abc'
            }
            query('test@example.test', db.session()).return_value = None
            with self.assertRaises(RasError):
                account_controller.post_respondent(payload)
            query.assert_called_once_with('test@example.test', db.session())
