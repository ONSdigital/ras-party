# pylint: disable=no-value-for-parameter

import json
import uuid
from test.mocks import MockRequests, MockResponse
from test.party_client import (PartyTestClient,
                               business_respondent_associations, businesses,
                               enrolments, respondents)
from test.test_data.default_test_values import (ALTERNATE_SURVEY_UUID,
                                                DEFAULT_BUSINESS_UUID,
                                                DEFAULT_RESPONDENT_UUID,
                                                DEFAULT_SURVEY_UUID)
from test.test_data.mock_enrolment import (MockEnrolmentDisabled,
                                           MockEnrolmentEnabled,
                                           MockEnrolmentPending)
from test.test_data.mock_respondent import (MockRespondent,
                                            MockRespondentWithId,
                                            MockRespondentWithIdActive,
                                            MockRespondentWithIdSuspended,
                                            MockRespondentWithPendingEmail)
from unittest import mock
from unittest.mock import MagicMock, patch

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from requests import Response
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from ras_party.controllers import account_controller, respondent_controller
from ras_party.controllers.queries import (query_business_by_party_uuid,
                                           query_respondent_by_party_uuid)
from ras_party.exceptions import RasNotifyError
from ras_party.models.models import (Business, BusinessRespondent, Enrolment,
                                     PendingEnrolment, Respondent,
                                     RespondentStatus)
from ras_party.support.public_website import PublicWebsite
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from ras_party.support.verification import generate_email_token


class TestRespondents(PartyTestClient):
    """Tests Respondent functionality , use respondent controller and account controller
    Python file name not changed so as to maintain git history"""

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests
        self.mock_notify = MagicMock()
        account_controller.NotifyGateway = MagicMock(return_value=self.mock_notify)
        self.mock_respondent = MockRespondent().attributes().as_respondent()
        self.mock_respondent_with_id = (
            MockRespondentWithId().attributes().as_respondent()
        )
        self.mock_respondent_with_id_suspended = (
            MockRespondentWithIdSuspended().attributes().as_respondent()
        )
        self.mock_respondent_with_id_active = (
            MockRespondentWithIdActive().attributes().as_respondent()
        )
        self.mock_respondent_with_pending_email = (
            MockRespondentWithPendingEmail().attributes().as_respondent()
        )
        self.respondent = None
        self.mock_enrolment_enabled = MockEnrolmentEnabled().attributes().as_enrolment()
        self.mock_enrolment_disabled = (
            MockEnrolmentDisabled().attributes().as_enrolment()
        )
        self.mock_enrolment_pending = MockEnrolmentPending().attributes().as_enrolment()

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
            "mark_for_deletion": respondent["mark_for_deletion"],
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
    def populate_business(self, session, business):
        self.business = Business(**business)
        session.add(self.business)

    @with_db_session
    def populate_with_pending_enrolment(self, session, enrolment=None):
        if not enrolment:
            enrolment = self.mock_enrolment_pending
        translated_enrolment = {
            "business_id": enrolment["business_id"],
            "respondent_id": enrolment["respondent_id"],
            "survey_id": enrolment["survey_id"],
            "case_id": "f8d7a5db-2b72-4409-b4d2-bc47b358cbda",
            "created_on": enrolment["created_on"],
        }
        self.enrolment = PendingEnrolment(**translated_enrolment)
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
        return frontstage_url.split("/")[-1]

    @staticmethod
    def generate_valid_token_for_email_change(email):
        frontstage_url = PublicWebsite().confirm_account_email_change_url(email)
        return frontstage_url.split("/")[-1]

    def test_get_respondent_with_invalid_id(self):
        self.get_respondent_by_id("123", 400)

    def test_get_respondent_with_valid_id(self):
        self.get_respondent_by_id(str(uuid.uuid4()), 404)

    def test_get_respondent_by_id_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.populate_with_respondent()
        # And we get the new respondent
        response = self.get_respondent_by_id(respondent.party_uuid)
        # Then the response matches the posted respondent
        self.assertTrue("id" in response)
        self.assertEqual(response["emailAddress"], self.mock_respondent["emailAddress"])
        self.assertEqual(response["firstName"], self.mock_respondent["firstName"])
        self.assertEqual(response["lastName"], self.mock_respondent["lastName"])
        self.assertEqual(
            response["sampleUnitType"], self.mock_respondent["sampleUnitType"]
        )
        self.assertEqual(response["telephone"], self.mock_respondent["telephone"])

    def test_get_respondent_by_ids_with_single_respondent_returns_correct_representation(
        self,
    ):
        # Given there is a respondent in the db
        respondent = self.populate_with_respondent()
        # And we get the new respondent
        ids = [respondent.party_uuid]
        response = self.get_respondents_by_ids(ids)
        # Then the response matches the posted respondent
        self.assertEqual(len(response), 1)
        self.assertEqual(
            response[0]["emailAddress"], self.mock_respondent["emailAddress"]
        )
        self.assertEqual(response[0]["firstName"], self.mock_respondent["firstName"])
        self.assertEqual(response[0]["lastName"], self.mock_respondent["lastName"])
        self.assertEqual(
            response[0]["sampleUnitType"], self.mock_respondent["sampleUnitType"]
        )
        self.assertEqual(response[0]["telephone"], self.mock_respondent["telephone"])

    def test_get_respondent_by_ids_returns_correct_representation(self):
        respondent_1 = MockRespondent()
        respondent_1.attributes(emailAddress="res1@example.com")

        respondent_2 = MockRespondent()
        respondent_2.attributes(emailAddress="res2@example.com")

        respondent_1 = self.populate_with_respondent(
            respondent=respondent_1.as_respondent()
        )
        respondent_2 = self.populate_with_respondent(
            respondent=respondent_2.as_respondent()
        )

        ids = [respondent_1.party_uuid, respondent_2.party_uuid]
        response = self.get_respondents_by_ids(ids)

        self.assertEqual(len(response), 2)

        self.assertTrue("id" in response[0])

        res_dict = {res["id"]: res for res in response}

        self.assertEqual(
            res_dict[respondent_1.party_uuid]["emailAddress"], "res1@example.com"
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["firstName"],
            self.mock_respondent["firstName"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["lastName"],
            self.mock_respondent["lastName"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["sampleUnitType"],
            self.mock_respondent["sampleUnitType"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["telephone"],
            self.mock_respondent["telephone"],
        )

        self.assertTrue("id" in response[1])
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["emailAddress"], "res2@example.com"
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["firstName"],
            self.mock_respondent["firstName"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["lastName"],
            self.mock_respondent["lastName"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["sampleUnitType"],
            self.mock_respondent["sampleUnitType"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["telephone"],
            self.mock_respondent["telephone"],
        )

        response = self.get_respondents_by_ids([respondent_1.party_uuid])

        self.assertEqual(len(response), 1)
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["emailAddress"], "res1@example.com"
        )

    def test_get_respondent_by_ids_with_only_unknown_id_returns_none(self):
        self.populate_with_respondent()
        party_uuid = str(uuid.uuid4())
        response = self.get_respondents_by_ids([party_uuid])
        self.assertEqual(len(response), 0)

    def test_get_respondent_by_ids_fails_if_id_is_not_uuid(self):
        self.populate_with_respondent()
        party_uuid = "gibberish"
        response = self.get_respondents_by_ids([party_uuid], expected_status=400)
        self.assertEqual(
            response["description"],
            """'gibberish' is not a valid UUID format for property 'id'""",
        )

    def test_get_respondents_using_complete_email_returns_respondent(self):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="a@z.com", expected_status=200
        )
        self.assertEqual(response["data"][0]["emailAddress"], "a@z.com")

    def test_get_respondents_using_partial_in_address_email_returns_respondent(self):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="@", expected_status=200
        )
        self.assertEqual(response["data"][0]["emailAddress"], "a@z.com")

    def test_get_respondents_using_partial_starting_address_email_returns_respondent(
        self,
    ):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="a", expected_status=200
        )
        self.assertEqual(response["data"][0]["emailAddress"], "a@z.com")

    def test_get_respondents_using_partial_ending_address_email_returns_respondent(
        self,
    ):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="m", expected_status=200
        )
        self.assertEqual(response["data"][0]["emailAddress"], "a@z.com")

    def test_get_respondents_using_unknown_address_email_returns_no_respondent(self):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="xx@yy.com", expected_status=200
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_complete_firstname_returns_respondent(self):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name="A", last_name=None, email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["firstName"], "A")

    def test_get_respondents_using_incorrect_case_complete_firstname_returns_respondent(
        self,
    ):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(firstName="Andrew")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name="andrew", last_name=None, email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["firstName"], "Andrew")

    def test_get_respondents_using_beginning_of_firstname_returns_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(firstName="Andrew")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name="Andr", last_name=None, email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["firstName"], "Andrew")

    def test_get_respondents_using_wildcard_in_firstname_returns_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(firstName="Andrew")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name="An%ew", last_name=None, email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["firstName"], "Andrew")

    def test_get_respondents_using_end_of_firstname_does_not_return_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(firstName="Andrew")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name="rew", last_name=None, email=None, expected_status=200
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_complete_lastname_returns_respondent(self):
        self.populate_with_respondent()
        response = self.get_respondents_by_name_email(
            first_name=None, last_name="Z", email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["lastName"], "Z")

    def test_get_respondents_using_beginning_of_lastname_returns_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(lastName="Torrance")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name=None, last_name="Torr", email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["lastName"], "Torrance")

    def test_get_respondents_using_wildcard_in_lastname_returns_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(lastName="Torrance")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name=None, last_name="To%ce", email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["lastName"], "Torrance")

    def test_get_respondents_using_beginning_of_lastname_incorrect_case_returns_respondent(
        self,
    ):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(lastName="Torrance")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name=None, last_name="ToRr", email=None, expected_status=200
        )
        self.assertEqual(response["data"][0]["lastName"], "Torrance")

    def test_get_respondents_using_end_of_lastname_does_not_return_respondent(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(lastName="Torrance")
        self.populate_with_respondent(respondent=mock_respondent.as_respondent())
        response = self.get_respondents_by_name_email(
            first_name=None, last_name="nce", email=None, expected_status=200
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_first_and_last_name_only_returns_matching_respondent(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew", last_name="Tor", email=None, expected_status=200
        )

        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Torrance")
        self.assertEqual(len(response["data"]), 1)

    def test_get_respondents_using_matching_first_and_not_matching_last_name_returns_no_respondent(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew", last_name="Williams", email=None, expected_status=200
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_matching_email_returns_respondent(self):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="Andrew.Smith@something.com",
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Smith")

    def test_get_respondents_using_non_matching_email_returns_no_respondent(self):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="Andrew.Williams@something.com",
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_matching_email_incorrect_case_returns_respondent(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="AnDREW.SmITH@Something.com",
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Smith")

    def test_get_respondents_using_partial_email_returns_respondent(self):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="Smith", expected_status=200
        )
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Smith")

    def test_get_respondents_using_wildcards_email_returns_respondent(self):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="And%Smith", expected_status=200
        )
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Smith")

    def test_get_respondents_using_non_matching_wildcards_email_does_not_return_respondent(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None, last_name=None, email="And%Will", expected_status=200
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondents_using_name_and_email_returns_only_the_respondent_that_match_all_params(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        mock_respondent3 = MockRespondent()
        mock_respondent3.attributes(
            firstName="Andrew",
            lastName="Williams",
            emailAddress="Andrew.Williamsh@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent3.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew", last_name="Sm", email="Andrew", expected_status=200
        )
        self.assertEqual(len(response["data"]), 1)
        self.assertEqual(response["data"][0]["firstName"], "Andrew")
        self.assertEqual(response["data"][0]["lastName"], "Smith")

    def test_get_respondents_using_name_and_email_returns_all_respondents_that_match(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Smith",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        mock_respondent3 = MockRespondent()
        mock_respondent3.attributes(
            firstName="Andrew",
            lastName="Thomas",
            emailAddress="Andrew.Thomas@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent3.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew", last_name="%T", email="Andrew", expected_status=200
        )
        self.assertEqual(len(response["data"]), 3)

    def test_get_respondents_using_name_and_email_returns_respondents_ordered_by_last_name_asc(
        self,
    ):
        mock_respondent1 = MockRespondent()
        mock_respondent1.attributes(
            firstName="Andrew",
            lastName="Gamma",
            emailAddress="Andrew.Torrance@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent1.as_respondent())

        mock_respondent2 = MockRespondent()
        mock_respondent2.attributes(
            firstName="Andrew",
            lastName="Alpha",
            emailAddress="Andrew.Smith@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent2.as_respondent())

        mock_respondent3 = MockRespondent()
        mock_respondent3.attributes(
            firstName="Andrew",
            lastName="Beta",
            emailAddress="Andrew.Thomas@something.com",
        )
        self.populate_with_respondent(respondent=mock_respondent3.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew", last_name=None, email="Andrew", expected_status=200
        )
        self.assertEqual(len(response["data"]), 3)
        self.assertEqual(response["data"][0]["lastName"], "Alpha")
        self.assertEqual(response["data"][1]["lastName"], "Beta")
        self.assertEqual(response["data"][2]["lastName"], "Gamma")

    def test_get_respondents_limit_returns_the_selected_number_of_respondents(self):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 10):
            mock_respondent.attributes(
                lastName=f"Torrance_{i}",
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew",
            last_name=None,
            email="Andrew",
            page=1,
            limit=6,
            expected_status=200,
        )

        self.assertEqual(len(response["data"]), 6)
        self.assertEqual(response["data"][0]["lastName"], "Torrance_0")
        self.assertEqual(response["data"][5]["lastName"], "Torrance_5")

    def test_get_respondents_limit_returns_the_available_respondents_if_less_than_limit(
        self,
    ):
        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 3):
            mock_respondent.attributes(
                lastName=f"Torrance_{i}",
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="Andrew",
            last_name=None,
            email="Andrew",
            page=1,
            limit=6,
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 3)

    def test_get_respondents_page_returns_the_expected_respondents(self):
        respondents_last_name = [
            f"{chr(i)}_Torrance" for i in range(ord("a"), ord("z") + 1)
        ]

        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 26):
            mock_respondent.attributes(
                firstName="Andrew",
                lastName=respondents_last_name[i],
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="Andrew",
            page=3,
            limit=6,
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 6)
        self.assertEqual(response["data"][0]["lastName"], "m_Torrance")
        self.assertEqual(response["data"][5]["lastName"], "r_Torrance")

    def test_get_respondents_page_returns_remaining_respondents_on_last_page(self):
        respondents_last_name = [
            f"{chr(i)}_Torrance" for i in range(ord("a"), ord("z") + 1)
        ]

        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 26):
            mock_respondent.attributes(
                firstName="Andrew",
                lastName=respondents_last_name[i],
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="Andrew",
            page=3,
            limit=12,
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 2)
        self.assertEqual(response["data"][0]["lastName"], "y_Torrance")
        self.assertEqual(response["data"][1]["lastName"], "z_Torrance")

    def test_get_respondents_total_represents_total_matching_records(self):
        respondents_last_name = [
            f"{chr(i)}_Torrance" for i in range(ord("a"), ord("z") + 1)
        ]

        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 26):
            first_name = "Andrew" if i % 5 else "fifthAndrew"
            mock_respondent.attributes(
                firstName=first_name,
                lastName=respondents_last_name[i],
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name="fifthAndrew",
            last_name=None,
            email=None,
            page=3,
            limit=2,
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 2)
        self.assertEqual(
            response["total"], 6
        )  # 0, 5, 10, 15, 20 and 25 should be 'fifthAndrew'

    def test_get_respondents_page_returns_zero_respondents_if_none_on_requested_page(
        self,
    ):
        respondents_last_name = [
            f"{chr(i)}_Torrance" for i in range(ord("a"), ord("z") + 1)
        ]

        mock_respondent = MockRespondent()
        mock_respondent.attributes(
            firstName="Andrew",
            lastName="Torrance",
            emailAddress="Andrew.Torrance@something.com",
        )
        for i in range(0, 26):
            mock_respondent.attributes(
                firstName="Andrew",
                lastName=respondents_last_name[i],
                emailAddress=f"Andrew_{i}.Torrance@something.com",
            )

            self.populate_with_respondent(respondent=mock_respondent.as_respondent())

        response = self.get_respondents_by_name_email(
            first_name=None,
            last_name=None,
            email="Andrew",
            page=22,
            limit=12,
            expected_status=200,
        )
        self.assertEqual(len(response["data"]), 0)

    def test_get_respondent_by_ids_with_an_unknown_id_still_returns_correct_representation_for_other_ids(
        self,
    ):
        respondent_1 = MockRespondent()
        respondent_1.attributes(emailAddress="res1@example.com")

        respondent_2 = MockRespondent()
        respondent_2.attributes(emailAddress="res2@example.com")

        respondent_1 = self.populate_with_respondent(
            respondent=respondent_1.as_respondent()
        )
        respondent_2 = self.populate_with_respondent(
            respondent=respondent_2.as_respondent()
        )

        response = self.get_respondents_by_ids(
            [respondent_1.party_uuid, respondent_2.party_uuid, str(uuid.uuid4())]
        )

        self.assertEqual(len(response), 2)

        self.assertTrue("id" in response[0])

        res_dict = {res["id"]: res for res in response}

        self.assertEqual(
            res_dict[respondent_1.party_uuid]["emailAddress"], "res1@example.com"
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["firstName"],
            self.mock_respondent["firstName"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["lastName"],
            self.mock_respondent["lastName"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["sampleUnitType"],
            self.mock_respondent["sampleUnitType"],
        )
        self.assertEqual(
            res_dict[respondent_1.party_uuid]["telephone"],
            self.mock_respondent["telephone"],
        )

        self.assertTrue("id" in response[1])
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["emailAddress"], "res2@example.com"
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["firstName"],
            self.mock_respondent["firstName"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["lastName"],
            self.mock_respondent["lastName"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["sampleUnitType"],
            self.mock_respondent["sampleUnitType"],
        )
        self.assertEqual(
            res_dict[respondent_2.party_uuid]["telephone"],
            self.mock_respondent["telephone"],
        )

    def test_get_respondent_with_invalid_email(self):
        payload = {"email": "123"}
        self.get_respondent_by_email(payload, 404)

    def test_get_respondent_by_email_returns_correct_representation(self):
        # Given there is a respondent in the db
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id_active
        )
        # And we get the new respondent
        request_json = {"email": respondent.email_address}
        response = self.get_respondent_by_email(request_json)
        # Then the response matches the posted respondent
        self.assertTrue("id" in response)
        self.assertEqual(
            response["emailAddress"],
            self.mock_respondent_with_id_active["emailAddress"],
        )
        self.assertEqual(
            response["firstName"], self.mock_respondent_with_id_active["firstName"]
        )
        self.assertEqual(
            response["lastName"], self.mock_respondent_with_id_active["lastName"]
        )
        self.assertEqual(
            response["sampleUnitType"],
            self.mock_respondent_with_id_active["sampleUnitType"],
        )
        self.assertEqual(
            response["telephone"], self.mock_respondent_with_id_active["telephone"]
        )

    def test_get_respondent_by_email_returns_404_for_no_respondent(self):
        # And we get the new respondent
        request_json = {"email": "h@6.com"}
        self.get_respondent_by_email(request_json, 404)

    def test_update_respondent_details_success(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        respondent_id = self.mock_respondent_with_id["id"]
        payload = {
            "firstName": "John",
            "lastName": "Snow",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "a@b.com",
        }
        self.change_respondent_details(respondent_id, payload, 200)

    def test_update_respondent_details_check_email(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        respondent_id = self.mock_respondent_with_id["id"]
        payload = {
            "firstName": "John",
            "lastName": "Snow",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "john.snow@thisemail.com",
        }
        self.change_respondent_details(respondent_id, payload, 200)

    def test_update_respondent_details_respondent_does_not_exist_error(self):
        respondent_id = "548df969-7c9c-4cd4-a89b-ac88cf0bfdf6"
        payload = {
            "firstName": "John",
            "lastName": "Bloggs",
            "telephone": "07837230942",
            "email_address": "a@b.com",
            "new_email_address": "a@b.com",
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
        self.assertTrue(self.mock_notify.request_to_notify.called)

    def test_resend_verification_email_responds_with_message(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
        # When the resend verification end point is hit
        response = self.resend_verification_email(respondent.party_uuid)
        # Message is present in response
        self.assertIn(account_controller.EMAIL_VERIFICATION_SENT, response["message"])

    def test_resend_verification_email_party_id_not_found(self):
        # Given the party_id sent doesn't exist
        # When the resend verification end point is hit
        response = self.resend_verification_email(DEFAULT_BUSINESS_UUID, 404)
        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertFalse(self.mock_notify.request_to_notify.called)
        self.assertIn(
            account_controller.NO_RESPONDENT_FOR_PARTY_ID, response["description"]
        )

    def test_resend_verification_email_party_id_malformed(self):
        self.resend_verification_email("malformed", 500)

    def test_resend_verification_email_sends_via_notify(self):
        # Given there is an enrolled respondent
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id
        )
        # When the resend verification email endpoint is hit
        self.resend_verification_email(respondent.party_uuid)
        # Then a notification message is sent to the respondent's current email address
        email = PublicWebsite().activate_account_url(respondent.email_address)
        personalisation = {"ACCOUNT_VERIFICATION_URL": email}
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=respondent.email_address,
            template_name="email_verification",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    def test_email_verification_expired_token_sends_calls_notify(self):
        # Given a token is used that has already been declared to be expired
        respondent = self.populate_with_respondent()
        token = self.generate_valid_token_from_email(respondent.email_address)
        # When the resend verification with expired token endpoint is hit
        self.resend_verification_email_expired_token(token)
        # Then a notification is sent the the respondent's email adddress
        self.assertTrue(self.mock_notify.request_to_notify.called)

    def test_resend_account_email_change_expired_token_sends_calls_notify(self):
        # Given a token is used that has already been declared to be expired
        my_respondent = MockRespondent()
        my_respondent.attributes(emailAddress="res2@example.com")
        my_respondent.attributes(pendingEmailAddress="res1@example.com")
        respondent = self.populate_with_respondent(
            respondent=my_respondent.as_respondent()
        )
        token = self.generate_valid_token_for_email_change("res1@example.com")
        # When the resend verification with expired token endpoint is hit
        self.resend_account_email_change_expired_token(token)
        # Then a notification is sent the the respondent's email adddress
        self.assertTrue(self.mock_notify.request_to_notify.called)

    def test_resend_account_email_change_expired_token_respondent_not_found(self):
        # The token is valid but the respondent doesn't exist
        current_app.config["EMAIL_TOKEN_EXPIRY"] = -1
        token = self.generate_valid_token_for_email_change("invalid@email.com")
        # When the resend verification with expired token endpoint is hit
        response = self.resend_account_email_change_expired_token(token, 404)
        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertFalse(self.mock_notify.request_to_notify.called)
        self.assertIn("Respondent does not exist", response["description"])

    def test_resend_verification_email_expired_token_respondent_not_found(self):
        # The token is valid but the respondent doesn't exist
        current_app.config["EMAIL_TOKEN_EXPIRY"] = -1
        token = self.generate_valid_token_from_email("invalid@email.com")
        # When the resend verification with expired token endpoint is hit
        response = self.resend_verification_email_expired_token(token, 404)
        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertFalse(self.mock_notify.request_to_notify.called)
        self.assertIn("Respondent does not exist", response["description"])

    def test_resend_verification_email_sends_to_new_email_address(self):
        # Given there is a respondent with a pending email address
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_pending_email
        )
        # When the resend verification email endpoint is hit
        self.resend_verification_email(respondent.party_uuid)
        # Then a notification message is sent to the pending email address and not the current one
        pending_email = PublicWebsite().activate_account_url(
            respondent.pending_email_address
        )
        personalisation = {"ACCOUNT_VERIFICATION_URL": pending_email}
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=respondent.pending_email_address,
            template_name="email_verification",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    def test_request_word_change_with_valid_email(self):
        respondent = self.populate_with_respondent()
        payload = {"email_address": respondent.email_address}
        self.request_password_change(payload)

    def test_request_password_change_active_account_calls_notify_gateway(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id_active
        )
        # When the request password end point is hit with an existing email address
        payload = {"email_address": respondent.email_address}
        self.request_password_change(payload)
        # Then a notification message is sent to the notify gateway
        personalisation = {
            "RESET_PASSWORD_URL": PublicWebsite().reset_password_url(
                respondent.email_address
            ),
            "FIRST_NAME": respondent.first_name,
        }
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=respondent.email_address,
            template_name="request_password_change",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    def test_request_password_change_created_account_doesnt_call_notify_gateway(self):
        # Given there is a respondent
        respondent = self.populate_with_respondent()
        # When the request password end point is hit with an existing email address
        payload = {"email_address": respondent.email_address}
        self.request_password_change(payload)
        self.mock_notify.request_for_notify.assert_not_called()

    def test_request_password_change_with_no_email(self):
        payload = {}
        self.request_password_change(payload, expected_status=400)

    def test_request_password_change_with_empty_email(self):
        payload = {"email_address": ""}
        self.request_password_change(payload, expected_status=404)

    def test_request_password_change_with_other_email(self):
        self.populate_with_respondent()
        payload = {"email_address": "not-mock@example.test"}
        self.request_password_change(payload, expected_status=404)
        self.assertFalse(self.mock_notify.request_for_notify.called)

    def test_request_password_change_with_malformed_email(self):
        payload = {"email_address": "malformed"}
        self.request_password_change(payload, expected_status=404)

    def test_should_reset_password_when_email_wrong_case(self):
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id_active
        )
        payload = {"email_address": respondent.email_address.upper()}
        self.request_password_change(payload)
        personalisation = {
            "RESET_PASSWORD_URL": PublicWebsite().reset_password_url(
                respondent.email_address
            ),
            "FIRST_NAME": respondent.first_name,
        }
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=respondent.email_address,
            template_name="request_password_change",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    @staticmethod
    def test_request_password_change_uses_case_insensitive_email_query():
        with patch(
            "ras_party.controllers.account_controller.query_respondent_by_email"
        ) as query, patch(
            "ras_party.support.session_decorator.current_app.db"
        ) as db, patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ), patch(
            "ras_party.controllers.account_controller.PublicWebsite"
        ):
            payload = {"email_address": "test@example.test"}
            account_controller.request_password_change(payload)
            query.assert_called_once_with("test@example.test", db.session())

    def test_change_password_with_no_password(self):
        # When the password is changed with a valid email and no password
        payload = {"email_address": "mock@email.com"}
        self.change_password(payload, expected_status=400)

    def test_change_password_with_no_respondent(self):
        # When the password is changed with no respondents in db
        payload = {
            "new_password": "password",
        }
        self.change_password(payload, expected_status=500)

    def test_change_password_with_valid_token(self):
        # Given a valid token from the respondent
        respondent = self.populate_with_respondent()
        payload = {
            "new_password": "password",
            "email_address": respondent.email_address,
        }
        # When the password is changed
        self.change_password(payload, expected_status=200)
        personalisation = {"FIRST_NAME": respondent.first_name}
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=respondent.email_address,
            template_name="confirm_password_change",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    @staticmethod
    def test_change_respondent_password_uses_case_insensitive_email_query():
        with patch(
            "ras_party.controllers.account_controller.query_respondent_by_email"
        ) as query, patch(
            "ras_party.support.session_decorator.current_app.db"
        ) as db, patch(
            "ras_party.controllers.account_controller.OauthClient"
        ) as client, patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ):
            client().update_account().status_code = 201
            account_controller.change_respondent_password(
                {"new_password": "abc", "email_address": "test@example.test"}
            )
            query.assert_called_once_with("test@example.test", db.session())

    def test_resend_password_email_expired_token_calls_notify(self):
        # Given a token is used that has already been declared to be expired
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id_active
        )
        token = self.generate_valid_token_from_email(respondent.email_address)
        # When the resend password with expired token endpoint is hit
        self.resend_password_email_expired_token(token)
        # Then a notification is sent the the respondent's email adddress
        self.assertTrue(self.mock_notify.request_to_notify.called)

    def test_resend_password_email_expired_token_respondent_not_found(self):
        # The token is valid but the respondent doesn't exist
        token = self.generate_valid_token_from_email("invalid@email.com")
        # When the resend verification with expired token endpoint is hit
        response = self.resend_password_email_expired_token(token, 404)
        # Then an email is not sent and a message saying there is no respondent is returned
        self.assertFalse(self.mock_notify.request_to_notify.called)
        self.assertIn("Respondent does not exist", response["description"])

    @staticmethod
    def test_change_respondent_password_ras_notify_error():
        with patch(
            "ras_party.controllers.account_controller.query_respondent_by_email"
        ) as query, patch(
            "ras_party.support.session_decorator.current_app.db"
        ) as db, patch(
            "ras_party.controllers.account_controller.OauthClient"
        ) as client, patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ) as notify:
            notify.side_effect = RasNotifyError(mock.Mock())
            client().update_account().status_code = 201
            account_controller.change_respondent_password(
                {"new_password": "abc", "email_address": "test@example.test"}
            )
            query.assert_called_once_with("test@example.test", db.session())

    def test_notify_account_lock(self):
        with patch("ras_party.controllers.account_controller.NotifyGateway"), patch(
            "ras_party.controllers.account_controller.PublicWebsite"
        ):
            self.populate_with_respondent(
                respondent=self.mock_respondent_with_id_suspended
            )
            party_id = self.mock_respondent_with_id["id"]
            db_respondent = respondents()[0]
            payload = {
                "respondent_id": party_id,
                "email_address": db_respondent.email_address,
                "status_change": "SUSPENDED",
            }
            self.put_respondent_account_status(payload, party_id, expected_status=200)

    def test_notify_account_lock_with_no_respondent(self):
        # When the account is locked with no respondents in db
        party_id = self.mock_respondent_with_id["id"]
        payload = {"email_address": "emailAddress.com"}
        self.put_respondent_account_status(payload, party_id, expected_status=400)

    def test_notify_account_ras_notify_error(self):
        with patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ) as notify, patch("ras_party.controllers.account_controller.PublicWebsite"):
            with self.assertLogs() as ctx:
                notify.side_effect = RasNotifyError(mock.Mock())
                self.populate_with_respondent(
                    respondent=self.mock_respondent_with_id_suspended
                )
                party_id = self.mock_respondent_with_id["id"]
                db_respondent = respondents()[0]
                payload = {
                    "respondent_id": party_id,
                    "email_address": db_respondent.email_address,
                    "status_change": "SUSPENDED",
                }
                self.put_respondent_account_status(payload, party_id)
                for logs in ctx.records:
                    if "ERROR" in logs.levelname:
                        self.assertIn(
                            "Error sending request to Notify Gateway", logs.message
                        )

    def test_verify_token_with_bad_secrets(self):
        # Given a respondent exists with an invalid token
        respondent = self.populate_with_respondent()
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(respondent.email_address, salt="salt")
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_bad_email(self):
        # Given a respondent in the db but other email
        self.populate_with_respondent()
        secret_key = current_app.config["SECRET_KEY"]
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(
            "not-mock@example.test", salt=current_app.config["EMAIL_TOKEN_SALT"]
        )
        # When the verify token endpoint is hit it errors
        self.verify_token(token, expected_status=404)

    def test_verify_token_with_valid_token(self):
        # Given respondent exists with a valid token
        respondent = self.populate_with_respondent()
        secret_key = current_app.config["SECRET_KEY"]
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(
            respondent.email_address, salt=current_app.config["EMAIL_TOKEN_SALT"]
        )
        # Then the verify end point verifies the token
        self.verify_token(token)

    @staticmethod
    def test_verify_token_uses_case_insensitive_email_query():
        with patch(
            "ras_party.controllers.account_controller.query_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            token = generate_email_token("test@example.test")
            account_controller.verify_token(token)
            query.assert_called_once_with("test@example.test", db.session())

    def test_put_respondent_email_returns_400_when_no_email(self):
        self.put_email_to_respondents({}, 400)

    def test_put_respondent_email_returns_400_when_no_new_email(self):
        put_data = {"email_address": self.mock_respondent["emailAddress"]}
        self.put_email_to_respondents(put_data, 400)

    def test_put_respondent_email_returns_404_when_no_respondent(self):
        put_data = {
            "email_address": self.mock_respondent["emailAddress"],
            "new_email_address": "test@example.test",
        }
        self.put_email_to_respondents(put_data, 404)

    def test_put_respondent_email_returns_respondent_same_email(self):
        self.populate_with_respondent()
        put_data = {
            "email_address": self.mock_respondent["emailAddress"],
            "new_email_address": self.mock_respondent["emailAddress"],
        }
        response = self.put_email_to_respondents(put_data)
        self.assertTrue(respondents()[0].email_address == response["emailAddress"])

    def test_put_respondent_email_returns_409_existing_email(self):
        respondent = self.populate_with_respondent()
        mock_respondent_b = self.mock_respondent.copy()
        mock_respondent_b["emailAddress"] = "test@example.test"
        self.populate_with_respondent(respondent=mock_respondent_b)

        put_data = {
            "email_address": respondent.email_address,
            "new_email_address": mock_respondent_b["emailAddress"],
        }
        self.put_email_to_respondents(put_data, 409)

    def test_put_respondent_email_new_email(self):
        self.populate_with_respondent()
        put_data = {
            "email_address": self.mock_respondent["emailAddress"],
            "new_email_address": "test@example.test",
        }
        self.put_email_to_respondents(put_data)
        self.assertEqual(respondents()[0].pending_email_address, "test@example.test")
        self.assertEqual(respondents()[0].email_address, "a@z.com")

    def test_put_respondent_email_calls_the_notify_service(self):
        respondent = self.populate_with_respondent(respondent=self.mock_respondent)
        put_data = {
            "email_address": self.mock_respondent["emailAddress"],
            "new_email_address": "test@example.test",
        }
        self.put_email_to_respondents(put_data)
        personalisation = {
            "ACCOUNT_VERIFICATION_URL": PublicWebsite().activate_account_url(
                "test@example.test"
            ),
        }
        self.mock_notify.request_to_notify.assert_called_once_with(
            email="test@example.test",
            template_name="email_verification",
            personalisation=personalisation,
            reference=respondent.party_uuid,
        )

    def test_email_verification_activates_a_respondent(self):
        self.populate_with_respondent()
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        response = self.put_email_verification(token, 200)
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.ACTIVE)
        self.assertEqual(response["status"], RespondentStatus.ACTIVE.name)

    def test_email_verification_url_is_from_config_yml_file(self):
        account_controller._send_email_verification(0, "test@example.test")
        expected_url = "http://dummy.ons.gov.uk/register/activate-account/"
        frontstage_url = self.mock_notify.request_to_notify.call_args[1][
            "personalisation"
        ]["ACCOUNT_VERIFICATION_URL"]
        self.assertIn(expected_url, frontstage_url)

    def test_email_verification_twice_produces_a_200(self):
        respondent = self.populate_with_respondent()
        token = self.generate_valid_token_from_email(respondent.email_address)
        self.put_email_verification(token, 200)
        response = self.put_email_verification(token, 200)
        self.assertEqual(response["status"], RespondentStatus.ACTIVE.name)

    def test_email_verification_bad_token_produces_a_404(self):
        secret_key = "fake_key"
        timed_serializer = URLSafeTimedSerializer(secret_key)
        token = timed_serializer.dumps(
            self.mock_respondent["emailAddress"], salt="salt"
        )
        self.put_email_verification(token, 404)

    def test_email_verification_expired_token_produces_a_409(self):
        respondent = self.populate_with_respondent()
        current_app.config["EMAIL_TOKEN_EXPIRY"] = -1
        token = self.generate_valid_token_from_email(respondent.email_address)
        self.put_email_verification(token, 409)

    def test_email_verification_unknown_email_produces_a_404(self):
        self.populate_with_respondent()
        token = self.generate_valid_token_from_email("test@example.test")
        self.put_email_verification(token, 404)
        db_respondent = respondents()[0]
        self.assertEqual(db_respondent.status, RespondentStatus.CREATED)

    def test_put_email_verification_uses_case_insensitive_email_query(self):
        with patch(
            "ras_party.controllers.account_controller.query_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            token = self.generate_valid_token_from_email("test@example.test")
            account_controller.put_email_verification(token)
            query.assert_called_once_with("test@example.test", db.session())

    def test_post_respondent_with_payload_returns_200(self):
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)

    def test_post_respondent_without_business_returns_500(self):
        self.assertEqual(len(businesses()), 0)
        self.post_to_respondents(self.mock_respondent, 500)

    def test_post_respondent_with_no_payload_returns_400(self):
        self.post_to_respondents(None, 400)

    def test_post_respondent_with_empty_payload_returns_400(self):
        self.post_to_respondents({}, 400)

    def test_post_respondent_not_uuid_400(self):
        self.mock_respondent["id"] = "123"
        self.post_to_respondents(self.mock_respondent, 400)

    def test_post_respondent_twice_400(self):
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)
        response = self.post_to_respondents(self.mock_respondent, 400)
        self.assertIn("Email address already exists", response["description"])

    def test_post_respondent_twice_different_email(self):
        self.populate_with_business()
        self.post_to_respondents(self.mock_respondent, 200)
        self.mock_respondent["emailAddress"] = "test@example.test"
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
        self.mock_requests.get.assert_called_once_with(
            "http://mockhost:1111/cases/iac/fb747cq725lj"
        )

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
        self.assertEqual(str(business_id), DEFAULT_BUSINESS_UUID)
        self.assertEqual(str(respondent_id), created_respondent["id"])

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
        self.assertEqual(str(enrolment.survey_id), DEFAULT_SURVEY_UUID)
        # And is linked to the created respondent
        self.assertEqual(
            str(enrolment.business_respondent.respondent.party_uuid),
            created_respondent["id"],
        )
        # And is linked to the given business
        self.assertEqual(
            str(enrolment.business_respondent.business.party_uuid),
            DEFAULT_BUSINESS_UUID,
        )

    def test_associations_populated_when_respondent_created(self):
        # Given there is a respondent associated with a business
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )

        # When we GET the respondent
        respondent = self.get_respondent_by_id(self.mock_respondent_with_id["id"])

        # Then the respondent has the correct details
        self.assertEqual(
            respondent["associations"][0]["businessRespondentStatus"], "CREATED"
        )

    def test_post_respondent_calls_the_notify_service(self):
        # Given there is a business
        self.populate_with_business()
        # When a new respondent is posted
        self.post_to_respondents(self.mock_respondent, 200)
        # Then the (mock) notify service is called
        v_url = PublicWebsite().activate_account_url(
            self.mock_respondent["emailAddress"]
        )
        personalisation = {
            "ACCOUNT_VERIFICATION_URL": v_url,
        }
        self.mock_notify.request_to_notify.assert_called_once_with(
            email=self.mock_respondent["emailAddress"],
            template_name="email_verification",
            personalisation=personalisation,
            reference=str(respondents()[0].party_uuid),
        )

    def test_post_respondent_uses_case_insensitive_email_query(self):
        with patch(
            "ras_party.controllers.queries.query_respondent_by_email"
        ) as query, patch(
            "ras_party.support.session_decorator.current_app.db"
        ) as db, patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ), patch(
            "ras_party.controllers.account_controller.Requests"
        ), patch(
            "ras_party.controllers.account_controller.request_iac"
        ) as requested_iac, patch(
            "ras_party.controllers.account_controller.disable_iac"
        ) as updated_iac:
            payload = {
                "emailAddress": "test@example.test",
                "firstName": "Joe",
                "lastName": "bloggs",
                "password": "secure",
                "telephone": "111",
                "enrolmentCode": "abc",
            }
            with open("test/test_data/get_active_iac.json") as fp:
                requested_iac.return_value = json.load(fp)
            with open("test/test_data/get_updated_iac.json") as fp:
                updated_iac.return_value = json.load(fp)
            query("test@example.test", db.session()).return_value = None
            with self.assertRaises(BadRequest):
                account_controller.post_respondent(payload)
            query.assert_called_once_with("test@example.test", db.session())

    def test_post_add_new_survey_no_respondent_business_association(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "party_id": self.mock_respondent_with_id["id"],
            "enrolment_code": self.mock_respondent_with_id["enrolment_code"],
        }
        self.add_survey(request_json, 200)

    def test_post_add_new_survey_respondent_business_association(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "party_id": self.mock_respondent_with_id["id"],
            "enrolment_code": self.mock_respondent_with_id["enrolment_code"],
        }
        self.add_survey(request_json, 200)

    def test_post_add_new_survey_missing_party_id_returns_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "enrolment_code": self.mock_respondent_with_id["enrolment_code"]
        }
        response = self.add_survey(request_json, 400)
        self.assertTrue(
            response["description"] == ["Required key 'party_id' is missing."]
        )

    def test_post_add_new_survey_missing_enrolment_code_returns_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "party_id": self.mock_respondent_with_id["id"],
        }

        response = self.add_survey(request_json, 400)
        self.assertTrue(
            response["description"] == ["Required key 'enrolment_code' is missing."]
        )

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
            "party_id": self.mock_respondent_with_id["id"],
            "enrolment_code": self.mock_respondent_with_id["enrolment_code"],
        }

        self.add_survey(request_json, 400)

    def test_post_add_survey_no_business_raise_Internal_server_error(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "party_id": self.mock_respondent_with_id["id"],
            "enrolment_code": self.mock_respondent_with_id["enrolment_code"],
        }
        self.add_survey(request_json, 500)

    def test_put_change_respondent_enrolment_status_disabled_success(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')

        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        self.populate_with_enrolment()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "respondent_id": self.mock_respondent_with_id["id"],
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "change_flag": "DISABLED",
        }
        self.put_enrolment_status(request_json, 200)

    def test_put_change_respondent_enrolment_status_enabled_success(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')

        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        enrolment = self.mock_enrolment_disabled
        self.populate_with_enrolment(enrolment=enrolment)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "respondent_id": self.mock_respondent_with_id["id"],
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "change_flag": "ENABLED",
        }
        self.put_enrolment_status(request_json, 200)

    def test_put_change_respondent_enrolment_status_no_respondent(self):
        request_json = {
            "respondent_id": self.mock_respondent_with_id["id"],
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": DEFAULT_SURVEY_UUID,
            "change_flag": "ENABLED",
        }
        self.put_enrolment_status(request_json, 404)

    def test_put_change_respondent_enrolment_status_bad_request(self):
        request_json = {
            "wrong_json": "wrong_json",
        }
        self.put_enrolment_status(request_json, 400)

    def test_put_change_respondent_enrolment_status_random_string_fail(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')

        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        self.populate_with_enrolment()
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        request_json = {
            "respondent_id": self.mock_respondent_with_id["id"],
            "business_id": DEFAULT_BUSINESS_UUID,
            "survey_id": ALTERNATE_SURVEY_UUID,
            "change_flag": "woafouewbhouGFHEPIW0",
        }
        self.put_enrolment_status(request_json, 500)

    @mock.patch(
        "ras_party.controllers.account_controller.get_case_id_for_business_survey"
    )
    @mock.patch("ras_party.controllers.case_controller.post_case_event")
    def test_disable_all_respondent_enrolments_disables_all_enrolments(
        self, mock_post_case, mock_get_case
    ):
        respondent_email = self._create_enrolments(second_enrolment_status="PENDING")
        response = self.patch_disable_all_respondent_enrolments(
            respondent_email, expected_status=200
        )
        assert response == {"message": "2 enrolments removed"}

    @mock.patch(
        "ras_party.controllers.account_controller.get_case_id_for_business_survey"
    )
    @mock.patch("ras_party.controllers.case_controller.post_case_event")
    def test_disable_all_respondent_enrolments_ignores_already_disabled_enrolments(
        self, mock_post_case, mock_get_case
    ):
        respondent_email = self._create_enrolments(second_enrolment_status="DISABLED")
        response = self.patch_disable_all_respondent_enrolments(
            respondent_email, expected_status=200
        )
        assert response == {"message": "1 enrolments removed"}

    def _create_enrolments(self, second_enrolment_status):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')

        respondent_id = self.mock_respondent_with_id["id"]
        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=respondent_id
        )
        self.populate_with_enrolment()
        # Add an enrolment for an alternate survey on same business
        enrolment = {
            "business_id": DEFAULT_BUSINESS_UUID,
            "respondent_id": 1,
            "survey_id": ALTERNATE_SURVEY_UUID,
            "status": second_enrolment_status,
            "created_on": "2017-12-01 13:40:55.495895",
        }
        self.populate_with_enrolment(enrolment=enrolment)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        return db_respondent.email_address

    def test_put_change_respondent_account_status_suspend(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id["id"]
        request_json = {
            "respondent_id": party_id,
            "email_address": db_respondent.email_address,
            "status_change": "SUSPENDED",
        }
        self.put_respondent_account_status(request_json, party_id, 200)

    def test_put_change_respondent_account_status_active(self):
        respondent = self.populate_with_respondent(
            respondent=self.mock_respondent_with_id
        )
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=respondent.party_uuid
        )
        enrolment = self.mock_enrolment_pending
        self.populate_with_enrolment(enrolment=enrolment)
        self.populate_with_pending_enrolment(enrolment=enrolment)
        request_json = {"status_change": "ACTIVE"}
        self.put_respondent_account_status(request_json, respondent.party_uuid, 200)

    def test_put_change_respondent_account_status_minus_status_change(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id_suspended["id"]
        request_json = {}
        self.put_respondent_account_status(request_json, party_id, 400)

    def test_put_change_respondent_account_status_no_respondent(self):
        party_id = self.mock_respondent_with_id["id"]
        request_json = {"status_change": "ACTIVE"}
        self.put_respondent_account_status(request_json, party_id, 404)

    def test_put_change_respondent_account_status_bad_oauth2_response(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id_suspended)
        db_respondent = respondents()[0]
        token = self.generate_valid_token_from_email(db_respondent.email_address)
        self.put_email_verification(token, 200)
        party_id = self.mock_respondent_with_id_suspended["id"]
        request_json = {"status_change": "ACTIVE"}

        response = Response()
        response.status_code = 401
        with patch(
            "ras_party.clients.oauth_client.OauthClient.update_account",
            return_value=response,
        ):
            self.put_respondent_account_status(request_json, party_id, 500)

    def test_change_respondent_password_bad_auth_response(self):
        with patch(
            "ras_party.controllers.account_controller.decode_email_token"
        ), patch("ras_party.controllers.account_controller.current_app"), patch(
            "ras_party.support.session_decorator.current_app.db"
        ), patch(
            "ras_party.controllers.account_controller.enrol_respondent_for_survey"
        ), patch(
            "ras_party.controllers.account_controller.NotifyGateway"
        ), patch(
            "ras_party.controllers.account_controller.OauthClient"
        ) as auth, patch(
            "ras_party.controllers.account_controller.Requests"
        ):
            payload = {"new_password": "password", "email_address": "mock@email.com"}
            auth().update_account().status_code.return_value = 500
            with self.assertRaises(InternalServerError):
                account_controller.change_respondent_password(payload)

    def test_update_verified_email_address_bad_auth_response(self):
        with patch("ras_party.controllers.account_controller.OauthClient") as auth:
            respondent = Respondent()

            auth().update_account().status_code.return_value = 500
            with self.assertRaises(InternalServerError):
                account_controller.update_verified_email_address(respondent, None)

    def test_validate_claim_returns_400_if_bus_id_missing(self):
        self.validate_respondent_claim("", "", "SomeSurveyId", expected_status=400)

    def test_validate_claim_returns_400_if_survey_id_missing(self):
        self.validate_respondent_claim("", "SomeBusId", "", expected_status=400)

    def test_validate_claim_returns_400_if_respondent_id_missing(self):
        self.validate_respondent_claim(
            "", "SomeBusId", "SomeSurveyId", expected_status=400
        )

    def test_validate_claim_returns_200_if_respondent_has_a_claim(self):

        self.populate_with_respondent(respondent=self.mock_respondent_with_id_active)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=DEFAULT_RESPONDENT_UUID
        )
        enrolment = self.mock_enrolment_enabled
        self.populate_with_enrolment(enrolment=enrolment)

        self.validate_respondent_claim(
            respondent_id=DEFAULT_RESPONDENT_UUID,
            business_id=DEFAULT_BUSINESS_UUID,
            survey_id=DEFAULT_SURVEY_UUID,
            expected_status=200,
            expected_result="Valid",
        )

    def test_validate_claim_returns_invalid_if_respondent_does_not_have_a_claim_on_specific_survey(
        self,
    ):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id_active)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=DEFAULT_RESPONDENT_UUID
        )
        enrolment = self.mock_enrolment_enabled
        self.populate_with_enrolment(enrolment=enrolment)

        self.validate_respondent_claim(
            respondent_id=DEFAULT_RESPONDENT_UUID,
            business_id=DEFAULT_BUSINESS_UUID,
            survey_id="ADifferentSurvey",
            expected_status=200,
            expected_result="Invalid",
        )

    def test_validate_claim_returns_invalid_if_respondent_does_not_have_a_claim_on_specific_business(
        self,
    ):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id_active)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=DEFAULT_RESPONDENT_UUID
        )
        enrolment = self.mock_enrolment_enabled
        self.populate_with_enrolment(enrolment=enrolment)

        self.validate_respondent_claim(
            respondent_id=DEFAULT_RESPONDENT_UUID,
            business_id="ADifferentBusiness",
            survey_id=DEFAULT_SURVEY_UUID,
            expected_status=200,
            expected_result="Invalid",
        )

    def test_validate_claim_returns_invalid_if_respondent_not_active(self):

        self.populate_with_respondent(respondent=self.mock_respondent_with_id_suspended)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=DEFAULT_RESPONDENT_UUID
        )
        enrolment = self.mock_enrolment_enabled
        self.populate_with_enrolment(enrolment=enrolment)

        self.validate_respondent_claim(
            respondent_id=DEFAULT_RESPONDENT_UUID,
            business_id=DEFAULT_BUSINESS_UUID,
            survey_id=DEFAULT_SURVEY_UUID,
            expected_status=200,
            expected_result="Invalid",
        )

    def test_validate_claim_returns_invalid_if_enrolment_not_enabled(self):

        self.populate_with_respondent(respondent=self.mock_respondent_with_id_active)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID, respondent_id=DEFAULT_RESPONDENT_UUID
        )
        enrolment = self.mock_enrolment_disabled
        self.populate_with_enrolment(enrolment=enrolment)

        self.validate_respondent_claim(
            respondent_id=DEFAULT_RESPONDENT_UUID,
            business_id=DEFAULT_BUSINESS_UUID,
            survey_id=DEFAULT_SURVEY_UUID,
            expected_status=200,
            expected_result="Invalid",
        )

    def test_account_view_auth_error_calls_rollback(self):
        # Given the database contains no enrolments
        self.assertEqual(len(enrolments()), 0)
        # And there is a business (related to the IAC code case context)
        self.populate_with_business()

        with patch(
            "ras_party.controllers.account_controller.OauthClient"
        ) as auth, patch("ras_party.controllers.account_controller.logger") as logger:
            auth().create_account().status_code = 500
            auth().create_account().content = {}

            # When a new respondent is posted
            self.post_to_respondents(self.mock_respondent, 200)
            logger.info.assert_any_call(
                "Registering respondent auth service responded with",
                content={},
                status=500,
            )

    def test_delete_respondent_by_email_user_does_not_exist(self):
        """A NotFound exception should be raised if the user can't be found"""
        with self.assertRaises(NotFound):
            respondent_controller.delete_respondent_by_email("does-not-exist@blah.com")

    def test_delete_respondent_by_email_sqlalchemyerror_on_commit(self):
        with patch(
            "ras_party.controllers.queries.query_single_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            query.return_value = {
                "party_uuid": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
                "email_address": "user@domain.com",
                "pending_email_address": "",
                "first_name": "Some",
                "last_name": "One",
                "telephone": "01271345820",
                "status": RespondentStatus.CREATED,
            }

            # This says db.session() returns an object that if commit is called on it (e.g., db.session().commit())
            # will raise a SQLAlchemyError.  The setup looks weird but none of the other varients seemed to work.
            db.configure_mock(
                **{
                    "session.return_value": MagicMock(
                        **{"commit.side_effect": SQLAlchemyError}
                    )
                }
            )
            with self.assertRaises(SQLAlchemyError):
                respondent_controller.delete_respondent_by_email("user@domain.com")
                db.rollback.assert_called_once()

    def test_delete_respondent_by_email_exception_on_commit(self):
        with patch(
            "ras_party.controllers.queries.query_single_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            query.return_value = {
                "party_uuid": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
                "email_address": "user@domain.com",
                "pending_email_address": "",
                "first_name": "Some",
                "last_name": "One",
                "telephone": "01271345820",
                "status": RespondentStatus.CREATED,
            }

            # This says db.session() returns an object that if commit is called on it (e.g., db.session().commit())
            # will raise an Exception.  The setup looks weird but none of the other varients seemed to work.
            db.configure_mock(
                **{
                    "session.return_value": MagicMock(
                        **{"commit.side_effect": Exception}
                    )
                }
            )
            with self.assertRaises(Exception):
                respondent_controller.delete_respondent_by_email("user@domain.com")
                db.rollback.assert_called_once()

    def test_update_respondent_mark_for_deletion_for_user_does_not_exists(self):
        """Given : The user email does not exists
        When : update_respondent_mark_for_deletion is called
        Then: A NotFound exception should be raised if the user can't be found
        """
        with self.assertRaises(NotFound):
            respondent_controller.delete_respondent_by_email("does-not-exist@blah.com")

    def test_update_respondent_mark_for_deletion_for_user_exception_on_commit(self):
        with patch(
            "ras_party.controllers.queries.query_single_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            query.return_value = {
                "party_uuid": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
                "email_address": "user@domain.com",
                "pending_email_address": "",
                "first_name": "Some",
                "last_name": "One",
                "telephone": "01271345820",
                "status": RespondentStatus.CREATED,
            }

            # This says db.session() returns an object that if commit is called on it (e.g., db.session().commit())
            # will raise an Exception.  The setup looks weird but none of the other varients seemed to work.
            db.configure_mock(
                **{
                    "session.return_value": MagicMock(
                        **{"commit.side_effect": Exception}
                    )
                }
            )
            with self.assertRaises(Exception):
                respondent_controller.update_respondent_mark_for_deletion(
                    "user@domain.com"
                )
                db.rollback.assert_called_once()

    def test_update_respondent_mark_for_deletion_for_user(self):
        respondent = self.populate_with_respondent()
        self.assertEqual(respondent.mark_for_deletion, False)
        respondent_controller.update_respondent_mark_for_deletion(
            respondent.email_address
        )
        response = self.get_respondent_by_id(respondent.party_uuid)
        self.assertEqual(response["markForDeletion"], True)

    def test_delete_respondent_mark_for_deletion(self):
        respondent = self.populate_with_respondent()
        self.assertEqual(respondent.mark_for_deletion, False)
        respondent_controller.update_respondent_mark_for_deletion(
            respondent.email_address
        )
        response_respondent = self.get_respondent_by_id(respondent.party_uuid)
        self.assertEqual(response_respondent["markForDeletion"], True)
        respondent_controller.delete_respondents_marked_for_deletion()
        with self.assertRaises(Exception):
            self.get_respondent_by_id(respondent.party_uuid)

    def test_batch_delete_user_data_marked_for_deletion(self):
        def mock_put_iac(*args, **kwargs):
            return MockResponse('{"active": false}')

        self.mock_requests.put = mock_put_iac
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        self.populate_with_business()
        self.associate_business_and_respondent(
            business_id=DEFAULT_BUSINESS_UUID,
            respondent_id=self.mock_respondent_with_id["id"],
        )
        self.populate_with_enrolment()
        respondent = respondents()[0]
        self.assertEqual(respondent.mark_for_deletion, False)
        respondent_controller.update_respondent_mark_for_deletion(
            respondent.email_address
        )
        response_respondent = self.get_respondent_by_id(respondent.party_uuid)
        self.assertEqual(response_respondent["markForDeletion"], True)
        respondent_1 = MockRespondent()
        respondent_1.attributes(emailAddress="res1@example.com", mark_for_deletion=True)
        respondent_1 = self.populate_with_respondent(
            respondent=respondent_1.as_respondent()
        )
        response = self.delete_user_data_marked_for_deletion()
        self.assertStatus(response, 204)
        with self.assertRaises(Exception):
            self.get_respondent_by_id(respondent.party_uuid)
        with self.assertRaises(Exception):
            self.get_respondent_by_email(respondent_1.email_address)

    def test_batch(self):
        respondent_0 = self.populate_with_respondent()
        respondent_1 = MockRespondent()
        respondent_1.attributes(emailAddress="res1@example.com")

        respondent_2 = MockRespondent()
        respondent_2.attributes(emailAddress="res2@example.com")

        respondent_1 = self.populate_with_respondent(
            respondent=respondent_1.as_respondent()
        )
        respondent_2 = self.populate_with_respondent(
            respondent=respondent_2.as_respondent()
        )

        self.assertEqual(respondent_0.mark_for_deletion, False)
        self.assertEqual(respondent_1.mark_for_deletion, False)
        self.assertEqual(respondent_2.mark_for_deletion, False)
        request = [
            {
                "method": "DELETE",
                "path": f"/party-api/v1/respondents/a@z.com",
                "headers": self.auth_headers,
            },
            {
                "method": "DELETE",
                "path": f"/party-api/v1/respondents/res1@example.com",
                "headers": self.auth_headers,
            },
            {
                "method": "DELETE",
                "path": f"/party-api/v1/respondents/res2@example.com",
                "headers": self.auth_headers,
            },
            {
                "method": "DELETE",
                "path": f"/party-api/v1/respondents/email/res3@example.com",
                "headers": self.auth_headers,
            },
        ]
        response = self.batch(request)
        expected_output = (
            '[{"status": 202}, {"status": 202}, {"status": 202}, {"status": 404}]'
        )
        self.assertEqual(expected_output, response)

    def test_multiple_delete(self):
        respondent_0 = self.populate_with_respondent()
        respondent_1 = MockRespondent()
        respondent_1.attributes(emailAddress="res1@example.com")

        respondent_2 = MockRespondent()
        respondent_2.attributes(emailAddress="res2@example.com")

        respondent_1 = self.populate_with_respondent(
            respondent=respondent_1.as_respondent()
        )
        respondent_2 = self.populate_with_respondent(
            respondent=respondent_2.as_respondent()
        )

        self.assertEqual(respondent_0.mark_for_deletion, False)
        self.assertEqual(respondent_1.mark_for_deletion, False)
        self.assertEqual(respondent_2.mark_for_deletion, False)
        users = ["a@z.com", "res1@example.com", "res2@example.com", "a@b.com"]
        for user in users:
            response = self.delete_user(f"/party-api/v1/respondents/{user}")
            if user != "a@b.com":
                self.assertEqual(202, response.status_code)
            else:
                self.assertEqual(404, response.status_code)

    def test_delete_returns_status_code_500_on_any_unhandled_error(self):
        with patch(
            "ras_party.controllers.queries.query_single_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            query.return_value = {
                "party_uuid": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
                "email_address": "user@domain.com",
                "pending_email_address": "",
                "first_name": "Some",
                "last_name": "One",
                "telephone": "01271345820",
                "status": RespondentStatus.CREATED,
            }

            # This says db.session() returns an object that if commit is called on it (e.g., db.session().commit())
            # will raise an Exception.  The setup looks weird but none of the other varients seemed to work.
            db.configure_mock(
                **{
                    "session.return_value": MagicMock(
                        **{"commit.side_effect": Exception}
                    )
                }
            )
            response = self.delete_user(f"/party-api/v1/respondents/user@domain.com")
            self.assertEqual(500, response.status_code)

    def test_delete_returns_status_code_500_on_sql_alchemy_error(self):
        with patch(
            "ras_party.controllers.queries.query_single_respondent_by_email"
        ) as query, patch("ras_party.support.session_decorator.current_app.db") as db:
            query.return_value = {
                "party_uuid": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
                "email_address": "user@domain.com",
                "pending_email_address": "",
                "first_name": "Some",
                "last_name": "One",
                "telephone": "01271345820",
                "status": RespondentStatus.CREATED,
            }

            # This says db.session() returns an object that if commit is called on it (e.g., db.session().commit())
            # will raise an Exception.  The setup looks weird but none of the other varients seemed to work.
            db.configure_mock(
                **{
                    "session.return_value": MagicMock(
                        **{"commit.side_effect": SQLAlchemyError}
                    )
                }
            )
            response = self.delete_user(f"/party-api/v1/respondents/user@domain.com")
            self.assertEqual(500, response.status_code)

    def test_respondent_emails_are_case_insensitive(self):
        self.populate_with_respondent()
        mock_respondent = self.mock_respondent.copy()
        mock_respondent["emailAddress"] = "A@z.com"
        self.post_to_respondents(payload=mock_respondent, expected_status=400)
