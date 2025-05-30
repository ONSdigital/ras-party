import json
from test.party_client import PartyTestClient
from unittest.mock import patch

from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

PARTY_UUID = "19eec8b9-0319-42db-ba61-6afa2cf77a26"
BUSINESS_ID = "4844b9ab-68b5-4f60-932b-b3da8df3d480"
SURVEY_ID = "17b4c9b3-58c2-4a53-991f-00541415b8c3"


class TestEnrolmentsView(PartyTestClient):

    @patch("ras_party.views.enrolments_view.respondent_enrolments")
    def test_get_enrolments(self, respondent_enrolments):
        enrolment_details = [
            {
                "business_name": "Business 1",
                "business_id": "75d9af56-1225-4d43-b41d-1199f5f89daa",
                "ru_ref": "001",
                "trading_as": "1 Business",
                "survey_details": [
                    {
                        "id": "9200d295-9d6e-41fe-b541-747ae67a279f",
                        "long_name": "Survey 1",
                        "short_name": "S1",
                        "ref": "S001",
                        "enrolment_status": "ENABLED",
                    }
                ],
            }
        ]
        respondent_enrolments.return_value = enrolment_details
        response = self.get_respondent_enrolments("b146f595-62a0-4d6d-ba88-ef40cffdf8a7")

        self.assertEqual(enrolment_details, json.loads(response.data))

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

    @patch("ras_party.views.enrolments_view.is_respondent_enrolled")
    def test_get_respondent_is_enrolments(self, is_respondent_enrolled):
        is_respondent_enrolled.return_value = True
        response = self.get_respondent_is_enrolments(PARTY_UUID, BUSINESS_ID, SURVEY_ID)

        self.assertEqual(200, response.status_code)
        self.assertEqual({"enrolled": True}, json.loads(response.data))

    @patch("ras_party.views.enrolments_view.is_respondent_enrolled")
    def test_get_respondent_is_enrolments_false(self, is_respondent_enrolled):
        is_respondent_enrolled.return_value = False
        response = self.get_respondent_is_enrolments(PARTY_UUID, BUSINESS_ID, SURVEY_ID)

        self.assertEqual(200, response.status_code)
        self.assertEqual({"enrolled": False}, json.loads(response.data))

    def test_get_respondent_is_enrolments_malformed(self):
        response = self.get_respondent_is_enrolments("malformed_id", BUSINESS_ID, SURVEY_ID)

        self.assertEqual(400, response.status_code)
