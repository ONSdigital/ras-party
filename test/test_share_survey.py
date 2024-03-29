import uuid
from test.mocks import MockRequests
from test.party_client import PartyTestClient
from test.test_data.default_test_values import (
    DEFAULT_BUSINESS_UUID,
    DEFAULT_RESPONDENT_UUID,
    DEFAULT_SURVEY_UUID,
)
from test.test_data.mock_business import MockBusiness
from test.test_data.mock_enrolment import (
    MockEnrolmentDisabled,
    MockEnrolmentEnabled,
    MockEnrolmentPending,
)
from test.test_data.mock_respondent import (
    MockNewRespondentWithId,
    MockRespondent,
    MockRespondentWithId,
    MockRespondentWithIdActive,
)
from unittest.mock import MagicMock, patch

from ras_party.controllers import account_controller
from ras_party.controllers.queries import (
    query_business_by_party_uuid,
    query_pending_surveys_by_business_and_survey,
    query_respondent_by_party_uuid,
)
from ras_party.models.models import (
    BusinessRespondent,
    Enrolment,
    PendingSurveys,
    Respondent,
    RespondentStatus,
)
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.verification import generate_email_token


class TestShareSurvey(PartyTestClient):
    """Tests share survey functionality"""

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests
        self.mock_respondent = MockRespondent().attributes().as_respondent()
        self.mock_respondent_with_id = MockRespondentWithId().attributes().as_respondent()
        self.mock_respondent_test_with_id = MockNewRespondentWithId().attributes().as_respondent()
        self.mock_respondent_with_id_active = MockRespondentWithIdActive().attributes().as_respondent()
        self.respondent = None
        self.mock_enrolment_enabled = MockEnrolmentEnabled().attributes().as_enrolment()
        self.mock_enrolment_disabled = MockEnrolmentDisabled().attributes().as_enrolment()
        self.mock_enrolment_pending = MockEnrolmentPending().attributes().as_enrolment()
        self.mock_pending_share = MockPendingShares().attributes().as_pending_shares()
        self.pending_share = None
        self.mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=self.mock_notify)

    @with_db_session
    def populate_pending_share(self, session):
        pending_share = self.mock_pending_share
        self.pending_share = PendingSurveys(**pending_share)
        session.add(self.pending_share)

    @with_db_session
    def populate_pending_survey(self, pending_survey, session):
        self.pending_share = PendingSurveys(**pending_survey)
        session.add(self.pending_share)

    @with_db_session
    def populate_with_respondent(self, session, respondent=None):
        if not respondent:
            respondent = self.mock_respondent
        translated_party = {
            "party_uuid": respondent.get("id") or str(uuid.uuid4()),
            "email_address": respondent["emailAddress"],
            "pending_email_address": respondent.get("pendingEmailAddress"),
            "first_name": respondent["firstName"],
            "last_name": respondent["lastName"],
            "telephone": respondent["telephone"],
            "status": respondent.get("status") or RespondentStatus.CREATED,
        }
        self.respondent = Respondent(**translated_party)
        session.add(self.respondent)
        account_controller.register_user(respondent)
        return self.respondent

    @with_db_session
    def populate_with_enrolment(self, session, enrolment=None):
        if not enrolment:
            enrolment = self.mock_enrolment_enabled
        translated_enrolment = {
            "business_id": enrolment["business_id"],
            "respondent_id": enrolment["respondent_id"],
            "survey_id": enrolment["survey_id"],
            "status": enrolment["status"],
            "created_on": enrolment["created_on"],
        }
        self.enrolment = Enrolment(**translated_enrolment)
        session.add(self.enrolment)

    @with_db_session
    def associate_business_and_respondent(self, business_id, respondent_id, session):
        business = query_business_by_party_uuid(business_id, session)
        respondent = query_respondent_by_party_uuid(respondent_id, session)

        br = BusinessRespondent(business=business, respondent=respondent)

        session.add(br)

    @with_db_session
    def is_pending_survey_registered(self, business_id, survey_id, session):
        pending_survey = query_pending_surveys_by_business_and_survey(business_id, survey_id, session, False)
        return True if pending_survey.count() != 0 else False

    def _make_business_attributes_active(self, mock_business):
        sample_id = mock_business["sampleSummaryId"]
        put_data = {"collectionExerciseId": "test_id"}
        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_share_survey_users_with_no_pending_share(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment()  # NOQA
        # When
        response = self.get_pending_survey_users(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID)
        # Then
        self.assertEqual(response, 1)

    def test_share_survey_users_with_pending_share(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment()  # NOQA
        self.populate_pending_share()
        # When
        response = self.get_pending_survey_users(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID)
        # Then
        self.assertEqual(response, 2)

    def test_share_survey_users_with_pending_share_bad_request(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment()  # NOQA
        self.populate_pending_share()
        # When
        response = self.get_pending_survey_users_bad_request()
        # Then
        self.assertEqual(response["description"], "Business id and Survey id is required for this request.")

    def test_share_survey_users_with_pending_share_not_found(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment()  # NOQA
        self.populate_pending_share()
        # When
        response = self.get_pending_survey_users_not_found("3b136c4b-7a14-4904-9e01-13364dd7b973", DEFAULT_SURVEY_UUID)
        # Then
        self.assertEqual(response["description"], "Business with party id does not exist")

    def test_share_survey_users_with_enrolment_disabled(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment(enrolment=self.mock_enrolment_disabled)  # NOQA
        self.populate_pending_share()
        # When
        response = self.get_pending_survey_users(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID)
        # Then
        self.assertEqual(response, 1)

    def test_share_survey_users_with_enrolment_pending(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_with_enrolment(enrolment=self.mock_enrolment_pending)  # NOQA
        self.populate_pending_share()
        # When
        response = self.get_pending_survey_users(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID)
        # Then
        self.assertEqual(response, 2)

    def test_post_pending_shares_success(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        # When
        payload = {
            "pending_shares": [
                {
                    "business_id": DEFAULT_BUSINESS_UUID,
                    "survey_id": DEFAULT_SURVEY_UUID,
                    "email_address": "test@test.com",
                    "shared_by": self.mock_respondent_with_id["id"],
                },
                {
                    "business_id": DEFAULT_BUSINESS_UUID,
                    "survey_id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef99",
                    "email_address": "test@test.com",
                    "shared_by": self.mock_respondent_with_id["id"],
                },
            ]
        }
        with patch("ras_party.views.pending_survey_view.send_pending_survey_email") as pending_share_email:
            response = self.post_pending_surveys(payload)
            # Then
            self.assertEqual(response, {"created": "success"})
            self.assertTrue(self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID))
            self.assertTrue(
                self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef99")
            )
            pending_share_email.assert_called()
            pending_share_email.assert_called_once()

    def test_post_pending_shares_fail_invalid_payload(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        # When
        payload = {}
        # Then
        response = self.post_pending_surveys_fail(payload)
        self.assertEqual(response["description"], "Payload Invalid - Pending survey key missing")

    def test_post_pending_shares_fail_invalid_payload_size(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        # When
        payload = {"pending_shares": []}
        # Then
        response = self.post_pending_surveys_fail(payload)
        self.assertEqual(response["description"], "Payload Invalid - pending_surveys list is empty")

    def test_post_pending_shares_fail_validation(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        # When
        payload = {
            "pending_shares": [
                {
                    "business_id": DEFAULT_BUSINESS_UUID,
                    "survey_id": DEFAULT_SURVEY_UUID,
                    "shared_by": self.mock_respondent_with_id["id"],
                },
                {
                    "business_id": DEFAULT_BUSINESS_UUID,
                    "survey_id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef99",
                    "email_address": "test@test.com",
                    "shared_by": self.mock_respondent_with_id["id"],
                },
            ]
        }
        # Then
        response = self.post_pending_surveys_fail(payload)
        self.assertEqual(response["description"], ["Required key 'email_address' is missing."])

    def test_delete_pending_shares_success(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_pending_share()
        self.assertTrue(self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID))
        with patch("ras_party.views.batch_request.send_share_survey_cancellation_emails") as pending_share_email:
            self.delete_pending_surveys()
            pending_share_email.assert_called()
            pending_share_email.assert_called_once()

    def test_share_survey_verification_token_success(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_pending_share()
        self.assertTrue(self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID))
        response = self.verify_pending_surveys(generate_email_token(str(self.mock_pending_share["batch_no"])))
        self.assertEqual(response[0]["batch_no"], str(self.mock_pending_share["batch_no"]))

    def test_share_survey_verification_token_fail(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.verify_pending_surveys(generate_email_token(str(self.mock_pending_share["batch_no"])), 404)

    def test_accept_share_survey_verification_success(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_pending_share()
        self.assertTrue(self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID))
        with patch("ras_party.controllers.pending_survey_controller.NotifyGateway") as pending_share_email:
            self.confirm_pending_survey(self.mock_pending_share["batch_no"])
        self.assertFalse(self.is_pending_survey_registered(DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID))
        self.assertEqual(pending_share_email.call_count, 1)

    def test_accept_share_survey_verification_fail(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.confirm_pending_survey(self.mock_pending_share["batch_no"], 404)

    def test_post_share_survey_respondent_success(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_pending_share()
        self.get_pending_surveys_with_batch_no(self.mock_pending_share["batch_no"])
        payload = {
            "emailAddress": "testing@test.com",
            "firstName": "Test",
            "lastName": "Test",
            "password": "Something",
            "telephone": "076843676789",
            "batch_no": str(self.mock_pending_share["batch_no"]),
        }
        with patch("ras_party.controllers.pending_survey_controller.NotifyGateway") as pending_share_email:
            self.post_pending_survey_respondent(payload=payload)
        self.get_respondent_by_email(payload={"email": "testing@test.com"})
        self.get_pending_surveys_with_batch_no(
            self.mock_pending_share["batch_no"], expected_status=404, expected_quantity=0
        )
        self.assertEqual(pending_share_email.call_count, 1)

    def test_post_share_survey_respondent_fail(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        self.populate_pending_share()
        self.get_pending_surveys_with_batch_no(self.mock_pending_share["batch_no"])
        payload = {
            "emailAddress": "testing@test.com",
            "firstName": "Test",
            "lastName": "Test",
            "telephone": "076843676789",
            "batch_no": str(self.mock_pending_share["batch_no"]),
        }
        self.post_pending_survey_respondent(payload=payload, expected_status=400)
        self.get_pending_surveys_with_batch_no(
            self.mock_pending_share["batch_no"], expected_status=200, expected_quantity=1
        )

    def test_get_pending_surveys_with_originator_respondent_party_id(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        mock_business_new = MockBusiness().as_business()
        mock_business_new["id"] = "3b136c4b-7a14-4904-9e01-13364dd7b973"
        self.post_to_businesses(mock_business_new, 200)
        self._make_business_attributes_active(mock_business=mock_business_new)
        self.associate_business_and_respondent(
            business_id=mock_business_new["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        batch_no = uuid.uuid1()
        mock_pending_survey_one = {
            "email_address": "test@test.com",
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        mock_pending_survey_two = {
            "email_address": "test@test.com",
            "business_id": "3b136c4b-7a14-4904-9e01-13364dd7b973",
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        self.populate_pending_survey(mock_pending_survey_one)
        self.populate_pending_survey(mock_pending_survey_two)

        self.get_pending_surveys_with_batch_no(batch_no, expected_status=200, expected_quantity=2)

        response = self.get_pending_surveys_with_originator_party_id(
            DEFAULT_RESPONDENT_UUID, expected_status=200, expected_quantity=2
        )
        self.assertEqual(response[0]["email_address"], mock_pending_survey_one["email_address"])
        self.assertEqual(response[0]["shared_by"], DEFAULT_RESPONDENT_UUID)
        self.assertEqual(response[1]["shared_by"], DEFAULT_RESPONDENT_UUID)

    def test_delete_pending_surveys_by_batch_number(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        mock_business_new = MockBusiness().as_business()
        mock_business_new["id"] = "3b136c4b-7a14-4904-9e01-13364dd7b973"
        self.post_to_businesses(mock_business_new, 200)
        self._make_business_attributes_active(mock_business=mock_business_new)
        self.associate_business_and_respondent(
            business_id=mock_business_new["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        batch_no = uuid.uuid1()
        mock_pending_survey_one = {
            "email_address": "test@test.com",
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        mock_pending_survey_two = {
            "email_address": "test@test.com",
            "business_id": "3b136c4b-7a14-4904-9e01-13364dd7b973",
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        self.populate_pending_survey(mock_pending_survey_one)
        self.populate_pending_survey(mock_pending_survey_two)

        self.get_pending_surveys_with_batch_no(batch_no, expected_status=200, expected_quantity=2)

        self.delete_pending_surveys_with_batch_no(batch_no)
        self.get_pending_surveys_with_batch_no(batch_no, expected_status=404, expected_quantity=0)
        self.delete_pending_surveys_with_batch_no(batch_no, expected_status=404)

    def test_resend_pending_surveys_email(self):
        # Given
        self.populate_with_respondent(respondent=self.mock_respondent_test_with_id)
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business["id"] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(
            business_id=mock_business["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        mock_business_new = MockBusiness().as_business()
        mock_business_new["id"] = "3b136c4b-7a14-4904-9e01-13364dd7b973"
        self.post_to_businesses(mock_business_new, 200)
        self._make_business_attributes_active(mock_business=mock_business_new)
        self.associate_business_and_respondent(
            business_id=mock_business_new["id"], respondent_id=self.mock_respondent_with_id["id"]
        )  # NOQA
        batch_no = uuid.uuid1()
        mock_pending_survey_one = {
            "email_address": "test@test.com",
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        mock_pending_survey_two = {
            "email_address": "test@test.com",
            "business_id": "3b136c4b-7a14-4904-9e01-13364dd7b973",
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": batch_no,
        }
        self.populate_pending_survey(mock_pending_survey_one)
        self.populate_pending_survey(mock_pending_survey_two)
        with patch("ras_party.views.pending_survey_view.NotifyGateway") as pending_share_email:
            not_found_response = self.post_resend_pending_surveys_email(
                payload={"batch_no": batch_no}, expected_status=400
            )
            self.assertEqual(pending_share_email.call_count, 0)
            self.assertEqual("Invalid request - batch_number missing", not_found_response["description"])
            invalid_request_response = self.post_resend_pending_surveys_email(
                payload={"batch_number": uuid.uuid1()}, expected_status=404
            )
            self.assertEqual("Batch number does not exist", invalid_request_response["description"])
            success_response = self.post_resend_pending_surveys_email(payload={"batch_number": batch_no})
            self.assertEqual("success", success_response["resend_pending_surveys_email"])


class MockPendingShares:
    def __init__(self):
        self._attributes = {
            "email_address": "test@test.com",
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "shared_by": DEFAULT_RESPONDENT_UUID,
            "batch_no": uuid.uuid1(),
        }

    def attributes(self, **kwargs):
        self._attributes.update(kwargs)
        return self

    def as_pending_shares(self):
        return self._attributes
