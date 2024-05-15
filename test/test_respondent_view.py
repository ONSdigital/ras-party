import json
from test.party_client import PartyTestClient
from test.test_data.default_test_values import (
    DEFAULT_BUSINESS_UUID,
    DEFAULT_SURVEY_UUID,
)
from test.test_data.mock_respondent import MockRespondent
from unittest.mock import patch

from ras_party.models.models import EnrolmentStatus


class TestRespondentView(PartyTestClient):

    @patch("ras_party.views.respondent_view.respondent_controller.get_respondents_by_survey_and_business_id")
    def test_get_respondents_by_business_and_survey_id(self, respondents_by_survey_and_business_id):
        # Given the return value of the controller is mocked to return a list of enrolled respondents
        respondents_enrolled = [
            {"respondent": MockRespondent().as_respondent(), "enrolment_status": EnrolmentStatus.ENABLED.name}
        ]
        respondents_by_survey_and_business_id.return_value = respondents_enrolled

        # When the end point is called
        response = self.get_respondents_by_survey_and_business_id(DEFAULT_SURVEY_UUID, DEFAULT_BUSINESS_UUID)

        # Then a 200 is returned with the correct list of Respondents
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), respondents_enrolled)

    def test_get_respondents_by_business_and_survey_id_invalid_uuid(self):
        # Given/When the end point is called with an invalid uuid for business_id
        response = self.get_respondents_by_survey_and_business_id(DEFAULT_SURVEY_UUID, "invalid_uuid")

        # Then a 400 is returned with description of the error
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, "Bad request, business or survey id not UUID")
