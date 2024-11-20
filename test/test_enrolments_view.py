import json
from test.party_client import PartyTestClient
from unittest.mock import patch

from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from ras_party.models.models import Enrolment, EnrolmentStatus


class TestEnrolmentsView(PartyTestClient):

    @patch("ras_party.views.enrolments_view.respondent_enrolments")
    def test_get_enrolments(self, respondent_enrolments):
        respondent_enrolments.return_value = [
            Enrolment(
                business_id="79af714a-ee1d-446c-9f39-763296ec1f05",
                survey_id="38553552-7d08-42e4-b86b-06f158c4b95e",
                respondent_id=1,
                status=EnrolmentStatus.ENABLED,
            )
        ]
        response = self.get_respondent_enrolments("b146f595-62a0-4d6d-ba88-ef40cffdf8a7")

        expected_response = [
            {
                "business_id": "79af714a-ee1d-446c-9f39-763296ec1f05",
                "survey_id": "38553552-7d08-42e4-b86b-06f158c4b95e",
                "status": "ENABLED",
            }
        ]

        self.assertEqual(expected_response, json.loads(response.data))

    @patch("ras_party.views.enrolments_view.respondent_enrolments")
    def test_get_enrolments_not_found_respondent(self, respondent_enrolments):
        respondent_enrolments.side_effect = NoResultFound
        response = self.get_respondent_enrolments("707778b9-cdb0-467a-9585-ee06bca47e2c")

        self.assertEqual(404, response.status_code)

    @patch("ras_party.views.enrolments_view.respondent_enrolments")
    def test_get_enrolments_data_error(self, respondent_enrolments):
        respondent_enrolments.side_effect = DataError("InvalidTextRepresentation", "party_uuid", "orig")
        response = self.get_respondent_enrolments("malformed_id")

        self.assertEqual(400, response.status_code)

    def test_get_enrolments_no_params(self):
        response = self.get_respondent_enrolments({})

        self.assertEqual(400, response.status_code)
