import datetime
import json
import os
import uuid
from unittest import TestCase
from unittest.mock import MagicMock

import responses

from config import TestingConfig
from ras_party.controllers import account_controller
from ras_party.models.models import Enrolment, Respondent
from run import create_app


# noinspection DuplicatedCode
class TestAccountController(TestCase):
    """
    Tests the functions in the account_controller.  Note, the __wrapped__ attribute allows us to get at the function
    without the need to mock the session object that's injected
    """

    def setUp(self):
        self.app = create_app("TestingConfig")

    project_root = os.path.dirname(os.path.dirname(__file__))
    valid_business_party_id = "3b136c4b-7a14-4904-9e01-13364dd7b972"
    valid_survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
    valid_case_id = "10b04906-f478-47f9-a985-783400dd8482"
    valid_case_group_id = "612f5c34-7e11-4740-8e24-cb321a86a917"
    valid_respondent_id = "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3"
    valid_payload = {
        "respondent_id": valid_respondent_id,
        "business_id": valid_business_party_id,
        "survey_id": valid_survey_id,
        "change_flag": "DISABLED",
    }
    url_request_collection_exercises_for_survey = (
        f"{TestingConfig.COLLECTION_EXERCISE_URL}/collectionexercises/survey/{valid_survey_id}"
    )
    url_request_casegroups_for_business = f"{TestingConfig.CASE_URL}/casegroups/partyid/{valid_business_party_id}"
    url_get_cases_for_casegroup = f"{TestingConfig.CASE_URL}/cases/casegroupid/{valid_case_group_id}"
    url_change_respondent_enrolment_status = f"{TestingConfig.CASE_URL}/cases/{valid_case_id}/events"

    with open(f"{project_root}/test_data/account/collection_exercises_for_survey.json") as fp:
        collex_for_survey = json.load(fp)
    with open(f"{project_root}/test_data/account/casegroups_for_business.json") as fp:
        business_casegroups = json.load(fp)
    with open(f"{project_root}/test_data/account/cases_for_casegroup.json") as fp:
        cases_for_casegroup = json.load(fp)

    def get_respondent_object(self):
        base = Respondent()
        base.id = "id"
        base.party_uuid = uuid.UUID(self.valid_business_party_id)
        base.status = 1  # ACTIVE
        base.email_address = "ons@fake.ons"
        base.pending_email_address = None
        base.first_name = "ONS"
        base.last_name = "User"
        base.telephone = "1234567890"
        base.mark_for_deletion = False
        base.created_on = datetime.datetime.strptime("2021-01-30 00:00:00", "%Y-%m-%d %H:%M:%S")
        return base

    def get_enrolment_object(self):
        base = Enrolment()
        base.business_id = uuid.UUID(self.valid_business_party_id)
        base.respondent_id = self.get_respondent_object().id
        base.survey_id = self.valid_survey_id
        base.status = 1  # ENABLED
        base.created_on = datetime.datetime.strptime("2021-01-30 00:00:00", "%Y-%m-%d %H:%M:%S")

    def test_change_respondent_enrolment_status_to_disabled(self):
        with responses.RequestsMock() as rsps:
            session = MagicMock()
            session.query().filter().first.return_value = self.get_respondent_object()
            session.query().filter().count.return_value = 0
            rsps.add(rsps.GET, self.url_request_collection_exercises_for_survey, json=self.collex_for_survey)
            rsps.add(rsps.GET, self.url_request_casegroups_for_business, json=self.business_casegroups)
            rsps.add(rsps.GET, self.url_get_cases_for_casegroup, json=self.cases_for_casegroup)
            rsps.add(rsps.POST, self.url_change_respondent_enrolment_status, json={}, status=200)
            with self.app.app_context():
                account_controller.change_respondent_enrolment_status.__wrapped__(self.valid_payload, session)

            rsps.assert_call_count(self.url_request_collection_exercises_for_survey, 1)
            rsps.assert_call_count(self.url_request_casegroups_for_business, 1)
            rsps.assert_call_count(self.url_get_cases_for_casegroup, 1)
            rsps.assert_call_count(self.url_request_collection_exercises_for_survey, 1)

    def test_change_respondent_enrolment_status_to_enabled(self):
        with responses.RequestsMock() as rsps:
            session = MagicMock()
            session.query().filter().first.return_value = self.get_respondent_object()
            session.query().filter().count.return_value = 1

            rsps.add(rsps.GET, self.url_request_collection_exercises_for_survey, json=self.collex_for_survey)
            rsps.add(rsps.GET, self.url_request_casegroups_for_business, json=self.business_casegroups)
            rsps.add(rsps.GET, self.url_get_cases_for_casegroup, json=self.cases_for_casegroup)
            rsps.add(rsps.POST, self.url_change_respondent_enrolment_status, json={}, status=200)
            with self.app.app_context():
                account_controller.change_respondent_enrolment_status.__wrapped__(self.valid_payload, session)
            rsps.assert_call_count(self.url_request_collection_exercises_for_survey, 1)
            rsps.assert_call_count(self.url_request_casegroups_for_business, 1)
            rsps.assert_call_count(self.url_get_cases_for_casegroup, 1)
            rsps.assert_call_count(self.url_request_collection_exercises_for_survey, 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
