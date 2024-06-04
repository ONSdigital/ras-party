import base64
import json
from test.fixtures import party_schema
from test.test_data.default_test_values import DEFAULT_BUSINESS_UUID
from test.test_data.mock_business import MockBusiness
from urllib.parse import urlencode

from flask import current_app
from flask_testing import TestCase
from sqlalchemy import text

from logger_config import logger_initial_config
from ras_party.models.models import Business, BusinessRespondent, Enrolment, Respondent
from ras_party.support.session_decorator import with_db_session
from run import create_app, create_database


@with_db_session
def businesses(session):
    return session.query(Business).all()


@with_db_session
def respondents(session):
    return session.query(Respondent).all()


@with_db_session
def business_respondent_associations(session):
    return session.query(BusinessRespondent).all()


@with_db_session
def enrolments(session):
    return session.query(Enrolment).all()


class PartyTestClient(TestCase):
    @staticmethod
    def create_app():
        app = create_app("TestingConfig")
        logger_initial_config(log_level=app.config["LOGGING_LEVEL"])
        app.config["PARTY_SCHEMA"] = party_schema.schema
        app.db = create_database(app.config["DATABASE_URI"], app.config["DATABASE_SCHEMA"])
        app.config["EMAIL_TOKEN_EXPIRY"] = 0
        return app

    def tearDown(self):
        connection = current_app.db.connect()
        connection.execute(text(f"drop schema {current_app.config['DATABASE_SCHEMA']} cascade;"))
        connection.commit()
        connection.close()

    def populate_with_business(self, business_id=DEFAULT_BUSINESS_UUID):
        mock_business = MockBusiness().as_business()
        mock_business["id"] = business_id
        self.post_to_businesses(mock_business, 200)

    @property
    def auth_headers(self):
        return {"Authorization": "Basic %s" % base64.b64encode(b"username:password").decode("ascii")}

    def post_to_parties(self, payload, expected_status):
        response = self.client.post(
            "/party-api/v1/parties",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def patch_to_parties(self, payload, expected_status):
        response = self.client.patch(
            "/party-api/v1/parties",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_businesses(self, payload, expected_status):
        response = self.client.post(
            "/party-api/v1/businesses",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_to_businesses_sample_link(self, sample_id, payload, expected_status=200):
        response = self.client.put(
            "/party-api/v1/businesses/sample/link/{}".format(sample_id),
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_to_respondents(self, payload, expected_status):
        response = self.client.post(
            "/party-api/v1/respondents",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_email_to_respondents(self, payload, expected_status=200):
        response = self.client.put(
            "/party-api/v1/respondents/email",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_id(self, id, expected_status=200, query_string=None):
        response = self.client.get(
            f"/party-api/v1/businesses/id/{id}", query_string=query_string, headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_businesses_by_ids(self, ids, expected_status=200):
        url_params = tuple(("id", id_param) for id_param in ids)
        url = "/party-api/v1/businesses?"
        url += urlencode(url_params)

        response = self.client.get(url, headers=self.auth_headers)

        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_business_by_ref(self, ref, expected_status=200, query_string=None):
        response = self.client.get(
            f"/party-api/v1/businesses/ref/{ref}", query_string=query_string, headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondents_by_ids(self, ids, expected_status=200):
        url_params = tuple(("id", id_param) for id_param in ids)
        url = "/party-api/v1/respondents?"
        url += urlencode(url_params)
        response = self.client.get(url, headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondents_by_name_email(self, first_name, last_name, email, page=1, limit=10, expected_status=200):
        url_params = {}

        url = "/party-api/v1/respondents?"
        if first_name:
            url_params["firstName"] = first_name

        if last_name:
            url_params["lastName"] = last_name

        if email:
            url_params["emailAddress"] = email

        if page:
            url_params["page"] = page

        if limit:
            url_params["limit"] = limit

        url += urlencode(url_params)

        response = self.client.get(url, headers=self.auth_headers)
        if expected_status:
            self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondent_by_id(self, id, expected_status=200):
        response = self.client.get(f"/party-api/v1/respondents/id/{id}", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_respondent_by_email(self, payload, expected_status=200):
        response = self.client.get(
            "/party-api/v1/respondents/email",
            data=json.dumps(payload),
            headers=self.auth_headers,
            content_type="application/json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_email_verification(self, token, expected_status):
        response = self.client.put(f"/party-api/v1/emailverification/{token}", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_verification_email(self, party_uuid, expected_status=200):
        response = self.client.post(f"/party-api/v1/resend-verification-email/{party_uuid}", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_account_email_change_verification_email_by_uuid(self, party_uuid, expected_status=200):
        response = self.client.post(
            f"/party-api/v1/resend-account-email-change-notification/{party_uuid}", headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_verification_email_expired_token(self, token, expected_status=200):
        response = self.client.post(
            f"/party-api/v1/resend-verification-email-expired-token/{token}", headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_account_email_change_expired_token(self, token, expected_status=200):
        response = self.client.post(
            f"/party-api/v1/resend-account-email-change-expired-token/{token}", headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def resend_password_email_expired_token(self, token, expected_status=200):
        response = self.client.post(
            f"/party-api/v1/resend-password-email-expired-token/{token}", headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def request_password_change(self, payload, expected_status=200):
        response = self.client.post(
            "/party-api/v1/respondents/request_password_change",
            data=json.dumps(payload),
            headers=self.auth_headers,
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def change_password(self, payload, expected_status=200):
        response = self.client.put(
            "/party-api/v1/respondents/change_password",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def verify_token(self, token, expected_status=200):
        response = self.client.get(f"/party-api/v1/tokens/verify/{token}", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def add_survey(self, payload, expected_status=200):
        response = self.client.post(
            "/party-api/v1/respondents/add_survey",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status)
        return json.loads(response.get_data(as_text=True))

    def get_businesses_search(self, expected_status=200, query_string=None, page=1, limit=100):
        response = self.client.get(
            f"/party-api/v1/businesses/search?query_string={query_string}&page={page}&limit={limit}",
            headers=self.auth_headers,
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def put_enrolment_status(self, payload, expected_status=200):
        response = self.client.put(
            "/party-api/v1/respondents/change_enrolment_status",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status)
        return json.loads(response.get_data(as_text=True))

    def patch_disable_all_respondent_enrolments(self, email_address, expected_status=200):
        response = self.client.patch(
            "/party-api/v1/respondents/disable-user-enrolments",
            data=json.dumps({"email": email_address}),
            headers=self.auth_headers,
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status)
        return json.loads(response.get_data(as_text=True))

    def put_respondent_account_status(self, payload, party_id, expected_status=200):
        response = self.client.put(
            f"/party-api/v1/respondents/edit-account-status/{party_id}",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status)
        return json.loads((response.get_data(as_text=True)))

    def change_respondent_details(self, respondent_id, payload, expected_status=200):
        response = self.client.put(
            f"/party-api/v1/respondents/id/{respondent_id}",
            headers=self.auth_headers,
            data=json.dumps(payload),
            content_type="application/vnd.ons.business+json",
        )
        self.assertStatus(response, expected_status)
        return response.get_data(as_text=True)

    def validate_respondent_claim(self, respondent_id, business_id, survey_id, expected_status, expected_result=None):
        url_params = {"respondent_id": respondent_id, "business_id": business_id, "survey_id": survey_id}

        url = "/party-api/v1/respondents/claim?"
        url += urlencode(url_params)
        response = self.client.get(url, headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        response_data = response.get_data().decode("utf-8")
        if expected_result:
            self.assertEqual(response_data, expected_result)
        return response_data

    def delete_user_data_marked_for_deletion(self, expected_status=204):
        response = self.client.delete("/party-api/v1/batch/respondents", headers=self.auth_headers)
        self.assertStatus(response, expected_status)
        return response

    def delete_user(self, url):
        response = self.client.delete(url, headers=self.auth_headers)
        return response

    def batch(self, payload, expected_status=207):
        response = self.client.post("/party-api/v1/batch/requests", headers=self.auth_headers, data=json.dumps(payload))
        self.assertStatus(response, expected_status)
        return response.get_data(as_text=True)

    def get_pending_survey_users(self, business_id, survey_id, is_transfer=False, expected_status=200):
        data = {"business_id": business_id, "survey_id": survey_id, "is_transfer": is_transfer}
        response = self.client.get(
            "/party-api/v1/pending-survey-users-count", query_string=data, headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_pending_survey_users_not_found(self, business_id, survey_id, expected_status=404):
        data = {
            "business_id": business_id,
            "survey_id": survey_id,
        }
        response = self.client.get(
            "/party-api/v1/pending-survey-users-count", query_string=data, headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def get_pending_survey_users_bad_request(self, expected_status=400):
        response = self.client.get("/party-api/v1/pending-survey-users-count", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_pending_surveys(self, payload, expected_status=201):
        response = self.client.post("/party-api/v1/pending-surveys", json=payload, headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def post_pending_surveys_fail(self, payload, expected_status=400):
        response = self.client.post("/party-api/v1/pending-surveys", json=payload, headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def delete_pending_surveys(self, expected_status=204):
        response = self.client.delete("/party-api/v1/batch/pending-surveys", headers=self.auth_headers)
        self.assertStatus(response, expected_status)

    def verify_pending_surveys(self, token, expected_status=200):
        self.app.config["EMAIL_TOKEN_EXPIRY"] = 36000
        response = self.client.get(f"/party-api/v1/pending-survey/verification/{token}", headers=self.auth_headers)
        self.assertStatus(response, expected_status, "Response body is : " + response.get_data(as_text=True))
        return json.loads(response.get_data(as_text=True))

    def confirm_pending_survey(self, batch_no, expected_status=201):
        self.app.config["EMAIL_TOKEN_EXPIRY"] = 36000
        response = self.client.post(
            f"/party-api/v1/pending-survey/confirm-pending-surveys/{batch_no}", headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, response.json)

    def post_pending_survey_respondent(self, payload, expected_status=201):
        response = self.client.post("/party-api/v1/pending-survey-respondent", json=payload, headers=self.auth_headers)
        self.assertStatus(response, expected_status, response.json)

    def post_resend_pending_surveys_email(self, payload, expected_status=201):
        response = self.client.post(
            "/party-api/v1/pending-surveys/resend-email", json=payload, headers=self.auth_headers
        )
        self.assertStatus(response, expected_status, response.json)
        return response.json

    def get_pending_surveys_with_batch_no(self, batch_no, expected_status=200, expected_quantity=1):
        response = self.client.get(f"/party-api/v1/pending-surveys/{batch_no}", headers=self.auth_headers)
        self.assertStatus(response, expected_status)
        if expected_quantity != 0:
            self.assertEqual(len(response.json), expected_quantity)

    def get_pending_surveys_with_originator_party_id(self, party_id, expected_status=200, expected_quantity=1):
        response = self.client.get(f"/party-api/v1/pending-surveys/originator/{party_id}", headers=self.auth_headers)
        self.assertStatus(response, expected_status)
        if expected_quantity != 0:
            self.assertEqual(len(response.json), expected_quantity)
        return response.json

    def delete_pending_surveys_with_batch_no(self, batch_no, expected_status=202):
        response = self.client.delete(f"/party-api/v1/pending-surveys/{batch_no}", headers=self.auth_headers)
        self.assertStatus(response, expected_status)

    def get_respondents_by_survey_and_business_id(self, survey_id, business_id):
        response = self.client.get(
            f"/party-api/v1/respondents/survey_id/{survey_id}/business_id/{business_id}", headers=self.auth_headers
        )
        return response
