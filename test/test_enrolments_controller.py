from test.party_client import PartyTestClient

from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from ras_party.controllers.enrolments_controller import enrolments_by_parameters
from ras_party.models.models import (
    Business,
    BusinessRespondent,
    Enrolment,
    EnrolmentStatus,
    Respondent,
)
from ras_party.support.session_decorator import with_db_session

respondents_enrolments = [
    {
        "respondent": "b6f9d6e8-b840-4c95-a6ce-9ef145dd1f85",
        "enrolment_details": [
            {
                "business": "75d9af56-1225-4d43-b41d-1199f5f89daa",
                "survey_id": "9200d295-9d6e-41fe-b541-747ae67a279f",
                "status": EnrolmentStatus.ENABLED,
            },
            {
                "business": "98e2c9dd-a760-47dd-ba18-439fd5fb93a3",
                "survey_id": "c641f6ad-a5eb-4d82-a647-7cd586549bbc",
                "status": EnrolmentStatus.ENABLED,
            },
        ],
    },
    {
        "respondent": "5718649e-30bf-4c25-a2c0-aaa733e54ed6",
        "enrolment_details": [
            {
                "business": "af25c9d5-6893-4342-9d24-4b88509e965f",
                "survey_id": "9200d295-9d6e-41fe-b541-747ae67a279f",
                "status": EnrolmentStatus.ENABLED,
            },
            {
                "business": "75d9af56-1225-4d43-b41d-1199f5f89daa",
                "survey_id": "9200d295-9d6e-41fe-b541-747ae67a279f",
                "status": EnrolmentStatus.DISABLED,
            },
        ],
    },
]


class TestEnrolments(PartyTestClient):

    def setUp(self):
        self._add_enrolments()

    def test_get_enrolments_party_id(self):
        enrolments = enrolments_by_parameters(party_uuid="b6f9d6e8-b840-4c95-a6ce-9ef145dd1f85")

        self.assertEqual(len(enrolments), 2)
        self.assertIn(str(enrolments[0].business_id), "75d9af56-1225-4d43-b41d-1199f5f89daa")
        self.assertIn(str(enrolments[1].business_id), "98e2c9dd-a760-47dd-ba18-439fd5fb93a3")

    def test_get_enrolments_business_id(self):
        enrolments = enrolments_by_parameters(business_id="75d9af56-1225-4d43-b41d-1199f5f89daa")

        self.assertEqual(len(enrolments), 2)
        self.assertIn(str(enrolments[0].survey_id), "9200d295-9d6e-41fe-b541-747ae67a279f")
        self.assertIn(str(enrolments[1].survey_id), "9200d295-9d6e-41fe-b541-747ae67a279f")

    def test_get_enrolments_survey_id(self):
        enrolments = enrolments_by_parameters(survey_id="9200d295-9d6e-41fe-b541-747ae67a279f")

        self.assertEqual(len(enrolments), 3)
        self.assertIn(str(enrolments[0].business_id), "75d9af56-1225-4d43-b41d-1199f5f89daa")
        self.assertIn(str(enrolments[1].business_id), "af25c9d5-6893-4342-9d24-4b88509e965f")
        self.assertIn(str(enrolments[2].business_id), "75d9af56-1225-4d43-b41d-1199f5f89daa")

    def test_get_enrolments_party_id_and_business_id_and_survey_id(self):
        enrolments = enrolments_by_parameters(
            party_uuid="b6f9d6e8-b840-4c95-a6ce-9ef145dd1f85",
            business_id="75d9af56-1225-4d43-b41d-1199f5f89daa",
            survey_id="9200d295-9d6e-41fe-b541-747ae67a279f",
        )

        self.assertEqual(len(enrolments), 1)
        self.assertIn(str(enrolments[0].respondent_id), "b6f9d6e8-b840-4c95-a6ce-9ef145dd1f85")
        self.assertIn(str(enrolments[0].business_id), "75d9af56-1225-4d43-b41d-1199f5f89daa")
        self.assertIn(str(enrolments[0].survey_id), "9200d295-9d6e-41fe-b541-747ae67a279f")

    def test_get_enrolments_party_id_enabled(self):
        enrolments = enrolments_by_parameters(
            party_uuid="5718649e-30bf-4c25-a2c0-aaa733e54ed6", status=EnrolmentStatus.ENABLED
        )

        self.assertEqual(len(enrolments), 1)
        self.assertIn(str(enrolments[0].business_id), "af25c9d5-6893-4342-9d24-4b88509e965f")
        self.assertIn(str(enrolments[0].survey_id), "9200d295-9d6e-41fe-b541-747ae67a279f")

    def test_get_enrolments_party_id_disabled(self):
        enrolments = enrolments_by_parameters(
            party_uuid="5718649e-30bf-4c25-a2c0-aaa733e54ed6", status=EnrolmentStatus.DISABLED
        )

        self.assertEqual(len(enrolments), 1)
        self.assertIn(str(enrolments[0].business_id), "75d9af56-1225-4d43-b41d-1199f5f89daa")
        self.assertIn(str(enrolments[0].survey_id), "9200d295-9d6e-41fe-b541-747ae67a279f")

    def test_get_enrolments_party_id_not_found_respondent(self):
        with self.assertRaises(NoResultFound):
            enrolments_by_parameters(party_uuid="e6a016da-f7e8-4cb0-88da-9d34a7c1382a")

    def test_get_enrolments_party_id_data_error(self):
        with self.assertRaises(DataError):
            enrolments_by_parameters(party_uuid="malformed_id")

    @with_db_session
    def _add_enrolments(self, session):
        businesses = {}

        for respondent_enrolments in respondents_enrolments:
            respondent = Respondent(party_uuid=respondent_enrolments["respondent"])
            session.add(respondent)

            for enrolment in respondent_enrolments["enrolment_details"]:
                if not (business := businesses.get(enrolment["business"])):
                    business = Business(party_uuid=enrolment["business"])
                    session.add(business)
                    businesses[enrolment["business"]] = business

                business_respondent = BusinessRespondent(business=business, respondent=respondent)
                session.add(business_respondent)
                session.flush()
                enrolment = Enrolment(
                    business_id=business.party_uuid,
                    survey_id=enrolment["survey_id"],
                    respondent_id=respondent.id,
                    status=enrolment["status"],
                )
                session.add(enrolment)
