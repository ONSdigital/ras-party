import json
from test.party_client import PartyTestClient
from test.test_data.default_test_values import (
    DEFAULT_BUSINESS_UUID,
    DEFAULT_SURVEY_UUID,
)
from test.test_data.mock_respondent import MockRespondent
from unittest.mock import patch


class TestParties(PartyTestClient):

    @patch("ras_party.views.respondent_view.respondent_controller.get_respondents_by_survey_and_business_id")
    def test_get_respondents_by_business_and_survey_id(self, testing):
        testing.return_value = [MockRespondent().as_respondent()]
        response = self.get_respondents_by_survey_and_business_id(DEFAULT_SURVEY_UUID, DEFAULT_BUSINESS_UUID)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [MockRespondent().as_respondent()])

    def test_get_respondents_by_business_and_survey_id_invalid_uuid(self):
        response = self.get_respondents_by_survey_and_business_id(DEFAULT_SURVEY_UUID, "invalid_uuid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, "Bad request, business or survey id not UUID")
