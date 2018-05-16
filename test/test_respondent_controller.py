# pylint: disable=no-value-for-parameter

import uuid
from unittest.mock import MagicMock, patch

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from ras_party.controllers import account_controller
from ras_party.controllers.queries import query_respondent_by_party_uuid, query_business_by_party_uuid
from ras_party.exceptions import RasError
from ras_party.models.models import BusinessRespondent, Enrolment, RespondentStatus, Respondent
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.transactional import transactional
from ras_party.support.verification import generate_email_token
from test.mocks import MockRequests, MockResponse
from test.party_client import PartyTestClient, respondents, businesses, business_respondent_associations, enrolments
from test.test_data.mock_enrolment import MockEnrolmentEnabled, MockEnrolmentDisabled
from test.test_data.mock_respondent import MockRespondent, MockRespondentWithId, \
    MockRespondentWithIdActive, MockRespondentWithIdSuspended


class TestRespondents(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests
        self.mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=self.mock_notify)
        self.mock_respondent = MockRespondent().attributes().as_respondent()
        self.mock_respondent_with_id = MockRespondentWithId().attributes().as_respondent()
        self.mock_respondent_with_id_suspended = MockRespondentWithIdSuspended().attributes().as_respondent()
        self.mock_respondent_with_id_active = MockRespondentWithIdActive().attributes().as_respondent()
        self.respondent = None
        self.mock_enrolment_enabled = MockEnrolmentEnabled().attributes().as_enrolment()
        self.mock_enrolment_disabled = MockEnrolmentDisabled().attributes().as_enrolment()

    @transactional
    @with_db_session
    def populate_with_respondent(self, tran, session, respondent=None):
        if not respondent:
            respondent = self.mock_respondent
        translated_party = {
            'party_uuid': respondent.get('id') or str(uuid.uuid4()),
            'email_address': respondent['emailAddress'],
            'first_name': respondent['firstName'],
            'last_name': respondent['lastName'],
            'telephone': respondent['telephone'],
            'status': respondent.get('status') or RespondentStatus.CREATED
        }
        self.respondent = Respondent(**translated_party)
        session.add(self.respondent)
        account_controller.register_user(respondent, tran)
        return self.respondent

    @with_db_session
    def populate_with_enrolment(self, session, enrolment=None):
        if not enrolment:
            enrolment = self.mock_enrolment_enabled
        translated_enrolment = {
            'business_id': enrolment['business_id'],
            'respondent_id': enrolment['respondent_id'],
            'survey_id': enrolment['survey_id'],
            'survey_name': enrolment['survey_name'],
            'status': enrolment['status'],
            'created_on': enrolment['created_on']
        }
        self.enrolment = Enrolment(**translated_enrolment)
        session.add(self.enrolment)

    @with_db_session
    def associate_business_and_respondent(self, business_id, respondent_id, session):
        business = query_business_by_party_uuid(business_id, session)
        respondent = query_respondent_by_party_uuid(respondent_id, session)

        br = BusinessRespondent(business=business, respondent=respondent)

        session.add(br)

    @staticmethod
    def generate_valid_token_from_email(email):
        frontstage_url = PublicWebsite().activate_account_url(email)
        return frontstage_url.split('/')[-1]

    def test_get_respondent_with_invalid_id(self):
        self.get_respondent_by_id('123', 400)

    def test_get_respondent_with_valid_id(self):
        self.get_respondent_by_id(str(uuid.uuid4()), 404)

    def test_get_respondent_by_id_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.populate_with_respondent()
        # And we get the new respondent
        response = self.get_respondent_by_id(respondent.party_uuid)
        # Then the response matches the posted respondent
        self.assertTrue('id' in response)
        self.assertEqual(response['emailAddress'], self.mock_respondent['emailAddress'])
        self.assertEqual(response['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response['telephone'], self.mock_respondent['telephone'])

    def test_get_respondent_by_ids_returns_correct_representation(self):
        respondent_1 = MockRespondent()
        respondent_1.attributes(email='res1@example.com')

        respondent_2 = MockRespondent()
        respondent_2.attributes(email='res2@example.com')

        self.populate_with_respondent(respondent=respondent_1.as_respondent())
        self.populate_with_respondent(respondent=respondent_2.as_respondent())

        self.assertNotEquals(respondent_1.party_uuid, respondent_2.party_uuid)
        response = self.get_respondent_by_ids(respondent_1.party_uuid + "," + respondent_2.party_uuid)

        self.assertEqualslen(len(response), 2)

        self.assertTrue('id' in response[0])
        self.assertEqual(response[0]['emailAddress'], 'res1@example.com')
        self.assertEqual(response[0]['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response[0]['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response[0]['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response[0]['telephone'], self.mock_respondent['telephone'])

        self.assertTrue('id' in response[1])
        self.assertEqual(response[1]['emailAddress'], 'res2@example.com')
        self.assertEqual(response[1]['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response[1]['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response[1]['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response[1]['telephone'], self.mock_respondent['telephone'])

    def test_get_respondent_by_ids_with_only_unknown_id_returns_none(self):
        respondent_1 = MockRespondent()
        respondent_1.attributes(email='res1@example.com')

        respondent_2 = MockRespondent()
        respondent_2.attributes(email='res2@example.com')

        self.populate_with_respondent(respondent=respondent_1.as_respondent())
        self.populate_with_respondent(respondent=respondent_2.as_respondent())

        self.assertNotEquals(respondent_1.party_uuid, respondent_2.party_uuid)
        response = self.get_respondent_by_ids(str(uuid.uuid4()))

        self.assertEqualslen(len(response), 0)

    def test_get_respondent_by_ids_with_unknown_id_returns_correct_representation(self):
        respondent_1 = MockRespondent()
        respondent_1.attributes(email='res1@example.com')

        respondent_2 = MockRespondent()
        respondent_2.attributes(email='res2@example.com')

        self.populate_with_respondent(respondent=respondent_1.as_respondent())
        self.populate_with_respondent(respondent=respondent_2.as_respondent())

        self.assertNotEquals(respondent_1.party_uuid, respondent_2.party_uuid)
        response = self.get_respondent_by_ids(respondent_1.party_uuid + ","
                                              + respondent_2.party_uuid + ","
                                              + str(uuid.uuid4()))

        self.assertEqualslen(len(response), 2)

        self.assertTrue('id' in response[0])
        self.assertEqual(response[0]['emailAddress'], 'res1@example.com')
        self.assertEqual(response[0]['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response[0]['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response[0]['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response[0]['telephone'], self.mock_respondent['telephone'])

        self.assertTrue('id' in response[1])
        self.assertEqual(response[1]['emailAddress'], 'res2@example.com')
        self.assertEqual(response[1]['firstName'], self.mock_respondent['firstName'])
        self.assertEqual(response[1]['lastName'], self.mock_respondent['lastName'])
        self.assertEqual(response[1]['sampleUnitType'], self.mock_respondent['sampleUnitType'])
        self.assertEqual(response[1]['telephone'], self.mock_respondent['telephone'])

    def test_get_respondent_with_invalid_email(self):
        payload = {
            "email": "123"
        }
        self.get_respondent_by_email(payload, 404)

    def test_get_respondent_by_email_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.populate_with_respondent(respondent=self.mock_respondent_with_id_active)
        # And we get the new respondent
        request_json = {
            'email': respondent.email_address
        }
        response = self.get_respondent_by_email(request_json)
        # Then the response matches the posted respondent
        self.assertTrue('id' in response)
        self.assertEqual(response['emailAddress'], self.mock_respondent_with_id_active['emailAddress'])
        self.assertEqual(response['firstName'], self.mock_respondent_with_id_active['firstName'])
        self.assertEqual(response['lastName'], self.mock_respondent_with_id_active['lastName'])
        self.assertEqual(response['sampleUnitType'], self.mock_respondent_with_id_active['sampleUnitType'])
        self.assertEqual(response['telephone'], self.mock_respondent_with_id_active['telephone'])

    def test_get_respondent_by_email_returns_404_for_no_respondent(self):
        # And we get the new respondent
        request_json = {
            'email': 'h@6.com'
        }
        self.get_respondent_by_email(request_json, 404)

    def test_update_respondent_details_success(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        respondent_id = self.mock_respondent_with_id['id']
        payload = {
            "firstName": "John",
            "lastName": "Snow",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "a@b.com"
            }
        self.change_respondent_details(respondent_id, payload, 200)

    def test_update_respondent_details_check_email(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        respondent_id = self.mock_respondent_with_id['id']
        payload = {
            "firstName": "John",
            "lastName": "Snow",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "john.snow@thisemail.com"
            }
        self.change_respondent_details(respondent_id, payload, 200)

    def test_update_respondent_details_respondent_does_not_exist_error(self):
        respondent_id = '548df969-7c9c-4cd4-a89b-ac88cf0bfdf6'
        payload = {
            "firstName": "John",
            "lastName": "Bloggs",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "a@b.com"
            }
        self.change_respondent_details(respondent_id, payload, 404)

    def test_resend_verification_email(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
        # When the resend verification end point is hit
        self.resend_verification_email(respondent.party_uuid)

    def test_resend_verification_email_calls_notify_gateway(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
        # When the resend verification end point is hit
        self.resend_verification_email(respondent.party_uuid)
        # Verification email is sent
        self.assertTrue(self.mock_notify.verify_email.called)

    def test_resend_verification_email_responds_with_message(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
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
        respondent = self.populate_with_respondent()
        payload = {'email_address': respondent.email_address}
        self.request_password_change(payload)

    def test_request_password_change_calls_notify_gateway(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
        # When the request password end point is hit with an existing email address
        payload = {'email_address': respondent.email_address}
        self.request_password_change(payload)
        # Then a notification message is sent to the notify gateway
        personalisation = {
            'RESET_PASSWORD_URL': PublicWebsite().reset_password_url(respondent.email_address),
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
        self.populate_with_respondent()
        payload = {'email_address': 'not-mock@example.test'}
        self.request_password_change(payload, expected_status=404)
        self.assertFalse(self.mock_notify.request_password_change.called)

    def test_request_password_change_with_malformed_email(self):
        payload = {'email_address': 'malformed'}
        self.request_password_change(payload, expected_status=404)

    def test_should_reset_password_when_email_wrong_case(self):
        respondent = self.populate_with_respondent()
        payload = {'email_address': respondent.email_address.upper()}
        self.request_password_change(payload)
        personalisation = {
            'RESET_PASSWORD_URL': PublicWebsite().reset_password_url(respondent.email_address),
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
        self.populate_with_respondent()
        token = self.generate_valid_token_from_email('not-mock@email.com')
        payload = {
            'new_password': '',
            'token': token
        }
        self.change_password(token, payload, expected_status=404)

    def test_change_password_with_other_token(self):
        # When the password is changed with a token that does not match respondent
        self.populate_with_respondent()
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
        respondent = self.populate_with_respondent()
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
            token = generate_email_token('test@example.test')
            client().update_account().status_code = 201
            account_controller.change_respondent_password(token, {'new_password': 'abc'})
            query.assert_called_once_with('test@example.test', db.session())

    def test_verify_token_with_bad_secrets(self):
        # Given a respondent exists with an invalid token
        respondent = self.populate_with_respondent()
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(respondent.email_address, salt='salt')
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_bad_email(self):
        # Given a respondent in the db but other email
        self.populate_with_respondent()
        secret_key = current_app.config['SECRET_KEY']
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps('not-mock@example.test', salt=current_app.config['EMAIL_TOKEN_SALT'])
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_valid_token(self):
        # Given respondent exists with a valid token
        respondent = self.populate_with_respondent()
        secret_key = current_app.config['SECRET_KEY']
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(respondent.email_address, salt=current_app.config['EMAIL_TOKEN_SALT'])
        # Then the verify end point verifies the token
        self.verify_token(token)

    @staticmethod
    def test_verify_token_uses_case_insensitive_email_query():
        with patch('ras_party.controllers.account_controller.query_respondent_by_email') as query,\
                patch('ras_party.support.session_decorator.current_app.db') as db:
            token = generate_email_token('test@example.test')
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
        self.populate_with_respondent()
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': self.mock_respondent['emailAddress'],
        }
        response = self.put_email_to_respondents(put_data)
        self.assertTrue(respondents()[0].email_address == response['emailAddress'])

    def test_put_respondent_email_returns_409_existing_email(self):
        respondent = self.populate_with_respondent()
        mock_respondent_b = self.mock_respondent.copy()
        mock_respondent_b['emailAddress'] = 'test@example.test'
        self.populate_with_respondent(respondent=mock_respondent_b)

        put_data = {
            'email_address': respondent.email_address,
            'new_email_address': mock_respondent_b['emailAddress'],
        }
        self.put_email_to_respondents(put_data, 409)

    def test_put_respondent_email_new_email(self):
        self.populate_with_respondent()
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': 'test@example.test',
        }
        self.put_email_to_respondents(put_data)
        self.assertEqual(respondents()[0].pending_email_address, 'test@example.test')
        self.assertEqual(respondents()[0].email_address, 'a@z.com')

    def test_put_respondent_email_calls_the_notify_service(self):
        respondent = self.populate_with_respondent(respondent=self.mock_respondent)
        put_data = {
            'email_address': self.mock_respondent['emailAddress'],
            'new_email_address': 'test@example.test'
        }
        self.put_email_to_respondents(put_data)
        personalisation = {
            'ACCOUNT_VERIFICATION_URL': PublicWebsite().activate_account_url('test@example.test'),
        }
        self.mock_notify.verify_email.assert_called_once_with(
            'test@example.test',
            personalisation,
            respondent.party_uuid
        )

    def test_email_verification_activates_a_respondent(self):
        self.populate_with_respondent()
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
        respondent = self.populate_with_respondent()
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
        self.populate_with_respondent()
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
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)

    def test_post_respondent_without_business_returns_404(self):
        self.assertEqual(len(businesses()), 0)
        self.post_to_respondents(self.mock_respondent, 404)

    def test_post_respondent_with_no_payload_returns_400(self):
        self.post_to_respondents(None, 400)

    def test_post_respondent_with_empty_payload_returns_400(self):
        self.post_to_respondents({}, 400)

    def test_post_respondent_not_uuid_400(self):
        self.mock_respondent['id'] = '123'
        self.post_to_respondents(self.mock_respondent, 400)

    def test_post_respondent_twice_400(self):
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)
        response = self.post_to_respondents(self.mock_respondent, 400)
        self.assertIn('Email address already exists', response['errors'][0])

    def test_post_respondent_twice_different_email(self):
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)
        self.mock_respondent['emailAddress'] = 'test@example.test'
        self.post_to_respondents(self.mock_respondent, 200)

    def test_post_respondent_with_inactive_iac(self):
        # Given the IAC code is inactive
        def mock_get_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.get = mock_get_iac
        # When a new respondent is posted
        # Then status code 400 is returned
        self.post_to_respondents(self.mock_respondent, 400)

    def test_post_respondent_requests_the_iac_details(self):
        # Given there is a business (related to the IAC code case context)
        self.populate_with_business()
        # When a new respondent is posted
        self.post_to_respondents(self.mock_respondent, 200)
        # Then the case service is called with the supplied IAC code
        self.mock_requests.get.assert_called_once_with('http://mockhost:1111/cases/iac/fb747cq725lj')

    def test_post_valid_respondent_adds_to_db(self):
        # Given the database contains no respondents
        self.assertEqual(len(respondents()), 0)
        # And there is a business (related to the IAC code case context)
        self.populate_with_business()
        # When a new respondent is posted
        self.post_to_respondents(self.mock_respondent, 200)
        # Then the database contains a respondent
        self.assertEqual(len(respondents()), 1)

    def test_post_respondent_creates_the_business_respondent_association(self):
        # Given the database contains no associations
        self.assertEqual(len(business_respondent_associations()), 0)
        # And there is a business (related to the IAC code case context)
        self.populate_with_business()
        # When a new respondent is posted
        created_respondent = self.post_to_respondents(self.mock_respondent, 200)
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
        self.populate_with_business()
        # When a new respondent is posted
        created_respondent = self.post_to_respondents(self.mock_respondent, 200)
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

    def test_associations_populated_when_respondent_created(self):
        # Given there is a respondent associated with a business
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])

        # When we GET the respondent
        respondent = self.get_respondent_by_id(self.mock_respondent_with_id['id'])

        # Then the respondent has the correct details
        self.assertEqual(respondent['associations'][0]['businessRespondentStatus'], "CREATED")

    def test_post_respondent_calls_the_notify_service(self):
        # Given there is a business
        self.populate_with_business()
        # When a new respondent is posted
        self.post_to_respondents(self.mock_respondent, 200)
        # Then the (mock) notify service is called
        v_url = PublicWebsite().activate_account_url(self.mock_respondent['emailAddress'])
        personalisation = {
            'ACCOUNT_VERIFICATION_URL': v_url,
        }
        self.mock_notify.verify_email.assert_called_once_with(
            self.mock_respondent['emailAddress'],
            personalisation,
            str(respondents()[0].party_uuid)
        )

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

    def test_post_add_new_survey_no_respondent_business_association(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'party_id': self.mock_respondent_with_id['id'],
            'enrolment_code': self.mock_respondent_with_id['enrolment_code']
        }
        self.add_survey(request_json, 200)

    def test_post_add_new_survey_respondent_business_association(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'party_id': self.mock_respondent_with_id['id'],
            'enrolment_code': self.mock_respondent_with_id['enrolment_code']
        }
        self.add_survey(request_json, 200)

    def test_post_add_new_survey_missing_party_id_returns_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'enrolment_code': self.mock_respondent_with_id['enrolment_code']
        }
        response = self.add_survey(request_json, 400)
        self.assertTrue(response['errors'] == ["Required key 'party_id' is missing."])

    def test_post_add_new_survey_missing_enrolment_code_returns_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'party_id': self.mock_respondent_with_id['id'],
        }

        response = self.add_survey(request_json, 400)
        self.assertTrue(response['errors'] == ["Required key 'enrolment_code' is missing."])

    def test_post_add_survey_inactive_enrolment_code(self):
        # Set IAC code to be inactive
        def mock_get_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.get = mock_get_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'party_id': self.mock_respondent_with_id['id'],
            'enrolment_code': self.mock_respondent_with_id['enrolment_code']
        }

        self.add_survey(request_json, 400)

    def test_post_add_survey_no_business_raise_ras_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'party_id': self.mock_respondent_with_id['id'],
            'enrolment_code': self.mock_respondent_with_id['enrolment_code']
        }
        self.add_survey(request_json, 404)

    def test_put_change_respondent_enrolment_status_disabled_success(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])
        self.populate_with_enrolment()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'respondent_id': self.mock_respondent_with_id['id'],
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
            'change_flag': 'DISABLED'
        }
        self.put_enrolment_status(request_json, 200)

    def test_put_change_respondent_enrolment_status_enabled_success(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])
        enrolment = self.mock_enrolment_disabled
        self.populate_with_enrolment(enrolment=enrolment)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'respondent_id': self.mock_respondent_with_id['id'],
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
            'change_flag': 'ENABLED'
        }
        self.put_enrolment_status(request_json, 200)

    def test_put_change_respondent_enrolment_status_no_respondent(self):
        request_json = {
            'respondent_id': self.mock_respondent_with_id['id'],
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
            'change_flag': 'ENABLED'
        }
        self.put_enrolment_status(request_json, 404)

    def test_put_change_respondent_enrolment_status_bad_request(self):
        request_json = {
            'wrong_json': 'wrong_json',
        }
        self.put_enrolment_status(request_json, 400)

    def test_put_change_respondent_enrolment_status_random_string_fail(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')
        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(business_id='3b136c4b-7a14-4904-9e01-13364dd7b972',
                                               respondent_id=self.mock_respondent_with_id['id'])
        self.populate_with_enrolment()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            'respondent_id': self.mock_respondent_with_id['id'],
            'business_id': '3b136c4b-7a14-4904-9e01-13364dd7b972',
            'survey_id': '02b9c366-7397-42f7-942a-76dc5876d86d',
            'change_flag': 'woafouewbhouGFHEPIW0'
        }
        self.put_enrolment_status(request_json, 500)

    def test_put_change_respondent_account_status_suspend(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id['id']
        request_json = {
            'status_change': 'SUSPENDED'
        }
        self.put_respondent_account_status(request_json, party_id, 200)

    def test_put_change_respondent_account_status_active(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id_suspended)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id_suspended['id']
        request_json = {
            'status_change': 'ACTIVE'
        }
        self.put_respondent_account_status(request_json, party_id, 200)

    def test_put_change_respondent_account_status_minus_status_change(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id_suspended['id']
        request_json = {

        }
        self.put_respondent_account_status(request_json, party_id, 400)

    def test_put_change_respondent_account_status_no_respondent(self):
        party_id = self.mock_respondent_with_id['id']
        request_json = {
            'status_change': 'ACTIVE'
        }
        self.put_respondent_account_status(request_json, party_id, 404)
