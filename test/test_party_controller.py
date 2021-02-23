import uuid

from ras_party.controllers import account_controller
from ras_party.controllers.queries import query_respondent_by_party_uuid, query_business_by_party_uuid
from ras_party.models.models import BusinessRespondent, Enrolment, Respondent, RespondentStatus
from ras_party.support.requests_wrapper import Requests
from ras_party.support.session_decorator import with_db_session
from test.mocks import MockRequests
from test.party_client import PartyTestClient, businesses
from test.test_data.mock_business import MockBusiness
from test.test_data.mock_respondent import MockRespondent, MockRespondentWithId, MockRespondentWithIdActive
from test.test_data.mock_enrolment import MockEnrolmentDisabled, MockEnrolmentEnabled, MockEnrolmentPending
from test.test_data.default_test_values import DEFAULT_BUSINESS_UUID, DEFAULT_SURVEY_UUID


class TestParties(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests
        self.mock_respondent = MockRespondent().attributes().as_respondent()
        self.mock_respondent_with_id = MockRespondentWithId().attributes().as_respondent()
        self.mock_respondent_with_id_active = MockRespondentWithIdActive().attributes().as_respondent()
        self.respondent = None
        self.mock_enrolment_enabled = MockEnrolmentEnabled().attributes().as_enrolment()
        self.mock_enrolment_disabled = MockEnrolmentDisabled().attributes().as_enrolment()
        self.mock_enrolment_pending = MockEnrolmentPending().attributes().as_enrolment()

    @with_db_session
    def populate_with_respondent(self, session, respondent=None):
        if not respondent:
            respondent = self.mock_respondent
        translated_party = {
            'party_uuid': respondent.get('id') or str(uuid.uuid4()),
            'email_address': respondent['emailAddress'],
            'pending_email_address': respondent.get('pendingEmailAddress'),
            'first_name': respondent['firstName'],
            'last_name': respondent['lastName'],
            'telephone': respondent['telephone'],
            'status': respondent.get('status') or RespondentStatus.CREATED
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
            'business_id': enrolment['business_id'],
            'respondent_id': enrolment['respondent_id'],
            'survey_id': enrolment['survey_id'],
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

    def _make_business_attributes_active(self, mock_business):
        sample_id = mock_business['sampleSummaryId']
        put_data = {'collectionExerciseId': 'test_id'}
        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

    def test_post_valid_party_adds_to_db(self):
        mock_party = MockBusiness().as_party()
        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)

    def test_get_business_by_id_returns_correct_representation(self):
        mock_business = MockBusiness().as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']
        self._make_business_attributes_active(mock_business)

        response = self.get_business_by_id(party_id)
        self.assertEqual(len(response.items()), 7)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), mock_business['sampleSummaryId'])
        self.assertEqual(response.get('name'), mock_business.get('name'))
        self.assertEqual(response.get('trading_as'), 'Tradstyle-1 Tradstyle-2 Tradstyle-3')

    def test_get_business_by_ids_returns_correct_representation(self):
        mock_business_1 = MockBusiness().as_business()
        mock_business_2 = MockBusiness().as_business()

        party_id_1 = self.post_to_businesses(mock_business_1, 200)['id']
        party_id_2 = self.post_to_businesses(mock_business_2, 200)['id']

        self._make_business_attributes_active(mock_business_1)
        self._make_business_attributes_active(mock_business_2)
        response = self.get_businesses_by_ids([party_id_1, party_id_2])
        self.assertEqual(len(response), 2)

        res_dict = {res['id']: res for res in response}

        self.assertEqual(res_dict[party_id_1].get('id'), party_id_1)
        self.assertEqual(res_dict[party_id_1].get('sampleSummaryId'), mock_business_1['sampleSummaryId'])
        self.assertEqual(res_dict[party_id_1].get('name'), mock_business_1.get('name'))

        self.assertEqual(res_dict[party_id_2].get('id'), party_id_2)
        self.assertEqual(res_dict[party_id_2].get('sampleSummaryId'), mock_business_2['sampleSummaryId'])
        self.assertEqual(res_dict[party_id_2].get('name'), mock_business_2.get('name'))

    def test_get_business_by_ids_with_an_unknown_id_still_returns_correct_representation_for_other_ids(self):
        mock_business_1 = MockBusiness().as_business()
        mock_business_2 = MockBusiness().as_business()

        party_id_1 = self.post_to_businesses(mock_business_1, 200)['id']
        party_id_2 = self.post_to_businesses(mock_business_2, 200)['id']
        self._make_business_attributes_active(mock_business_2)
        self._make_business_attributes_active(mock_business_1)

        response = self.get_businesses_by_ids([party_id_1, party_id_2, str(uuid.uuid4())])
        self.assertEqual(len(response), 2)

        res_dict = {res['id']: res for res in response}

        self.assertEqual(res_dict[party_id_1].get('id'), party_id_1)
        self.assertEqual(res_dict[party_id_1].get('sampleSummaryId'), mock_business_1['sampleSummaryId'])
        self.assertEqual(res_dict[party_id_1].get('name'), mock_business_1.get('name'))

        self.assertEqual(res_dict[party_id_2].get('id'), party_id_2)
        self.assertEqual(res_dict[party_id_2].get('sampleSummaryId'), mock_business_2['sampleSummaryId'])
        self.assertEqual(res_dict[party_id_2].get('name'), mock_business_2.get('name'))

    def test_get_business_by_ids_with_only_an_unknown_id_returns_nothing(self):
        response = self.get_businesses_by_ids([str(uuid.uuid4())])
        self.assertEqual(len(response), 0)

    def test_get_business_by_ids_fails_if_id_is_not_uuid(self):
        party_uuid = "gibberish"
        response = self.get_businesses_by_ids([party_uuid], expected_status=400)
        self.assertEqual(response['description'], """'gibberish' is not a valid UUID format for property 'id'""")

    def test_get_business_by_id_with_no_active_attributes_returns_404(self):
        mock_business = MockBusiness().as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        self.get_business_by_id(party_id, 404)

    def test_get_business_by_id_and_collection_exercise_returns_correct_representation(self):
        # Post business and link to sample/collection exercise
        mock_business = MockBusiness().as_business()
        self.post_to_businesses(mock_business, 200)
        sample_id = mock_business['sampleSummaryId']
        put_data = {'collectionExerciseId': 'test_id'}
        self.put_to_businesses_sample_link(sample_id, put_data, 200)

        # Repost business and link to different sample/collection exercise
        mock_business['sampleSummaryId'] = '100000001'
        party_id = self.post_to_businesses(mock_business, 200)['id']
        put_data = {'collectionExerciseId': 'other_test_id'}
        self.put_to_businesses_sample_link('100000001', put_data, 200)

        # Retrieve data for first collection exercise
        response = self.get_business_by_id(party_id, query_string={"collection_exercise_id": "test_id"})
        self.assertEqual(len(response.items()), 7)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), sample_id)
        self.assertEqual(response.get('name'), mock_business.get('name'))
        self.assertEqual(response.get('trading_as'), 'Tradstyle-1 Tradstyle-2 Tradstyle-3')

        # Retrieve data for 2nd collection exercise
        response = self.get_business_by_id(party_id, query_string={"collection_exercise_id": "other_test_id"})
        self.assertEqual(len(response.items()), 7)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), '100000001')
        self.assertEqual(response.get('name'), mock_business.get('name'))
        self.assertEqual(response.get('trading_as'), 'Tradstyle-1 Tradstyle-2 Tradstyle-3')

    def test_get_business_by_id_returns_correct_representation_verbose(self):
        mock_business = MockBusiness().as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']
        self._make_business_attributes_active(mock_business)

        response = self.get_business_by_id(party_id, query_string={"verbose": "true"})
        self.assertTrue(len(response.items()) >= len(mock_business.items()))

    def test_put_business_sample_link_200(self):
        mock_business = MockBusiness().as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

        sample_id = mock_business['sampleSummaryId']
        put_data = {'collectionExerciseId': 'somecollectionexcid'}

        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_put_business_sample_link_returns_400_when_no_ce(self):
        mock_business = MockBusiness().as_business()
        sample_id = mock_business['sampleSummaryId']
        self.put_to_businesses_sample_link(sample_id, {}, 400)

    # TODO: Uncomment test and fix
    # def test_get_business_by_ref_returns_correct_representation_verbose(self):
    #     mock_business = MockBusiness().as_business()
    #     self.post_to_businesses(mock_business, 200)
    #     self._make_business_attributes_active(mock_business)
    #
    #     response = self.get_business_by_ref(mock_business['sampleUnitRef'])
    #
    #     del mock_business['sampleSummaryId']
    #     for x in mock_business:
    #         self.assertIn(x, response)

    def test_get_party_by_id_returns_correct_representation(self):
        mock_party_b = MockBusiness().as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']
        self._make_business_attributes_active(mock_party_b)

        response = self.get_party_by_id('B', party_id_b)

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_get_party_by_id_no_active_attributes_returns_404(self):
        mock_party_b = MockBusiness().as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        self.get_party_by_id('B', party_id_b, 404)

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness().as_party()
        self.post_to_parties(mock_party_b, 200)
        self._make_business_attributes_active(mock_party_b)
        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness().attributes(version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_existing_party_can_be_updated(self):
        mock_party = MockBusiness().attributes(version=1)

        response_1 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_party.attributes(version=2)
        response_2 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_post_businesses_with_no_body_returns_400(self):
        self.post_to_businesses(None, 400)

    def test_post_party_with_no_body_returns_400(self):
        self.post_to_parties(None, 400)

    def test_post_party_with_bad_schema_returns_400(self):
        self.post_to_parties({'bad': 'schema'}, 400)

    def test_post_businesses_with_bad_schema_returns_400(self):
        self.post_to_businesses({'bad': 'schema'}, 400)

    def test_get_business_with_invalid_id(self):
        self.get_business_by_id('123', 400)

    def test_get_nonexistent_business_by_id(self):
        party_id = uuid.uuid4()
        self.get_business_by_id(party_id, 404)

    def test_get_nonexistent_business_by_ref(self):
        self.get_business_by_ref('123', 404)

    def test_post_invalid_party(self):
        mock_party = MockBusiness().as_party()
        del mock_party['sampleUnitRef']
        self.post_to_parties(mock_party, 400)

    def test_get_party_with_invalid_unit_type(self):
        self.get_party_by_id('XX', '123', 400)

    def test_get_party_with_nonexistent_ref(self):
        self.get_party_by_ref('B', '123', 404)

    def test_get_party_by_survey_id_and_enrolment_statuses_with_valid_enrolment(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)  # NOQA
        mock_business = MockBusiness().as_business()
        mock_business['id'] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(business_id=mock_business['id'],
                                               respondent_id=self.mock_respondent_with_id['id'])  # NOQA
        self.populate_with_enrolment()  # NOQA
        self.get_party_by_id_filtered_by_survey_and_enrolment('B', mock_business['id'],
                                                              DEFAULT_SURVEY_UUID,
                                                              ['ENABLED', 'PENDING'])

    def test_get_party_by_survey_id_and_enrolment_statuses_with_invalid_enrolment(self):
        self.populate_with_respondent(respondent=self.mock_respondent_with_id)
        mock_business = MockBusiness().as_business()
        mock_business['id'] = DEFAULT_BUSINESS_UUID
        self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business=mock_business)
        self.associate_business_and_respondent(business_id=mock_business['id'],
                                               respondent_id=self.mock_respondent_with_id['id'])
        self.populate_with_enrolment(enrolment=self.mock_enrolment_disabled)  # NOQA
        self.get_party_by_id_filtered_by_survey_and_enrolment('B', mock_business['id'],
                                                              DEFAULT_SURVEY_UUID,
                                                              ['ENABLED', 'PENDING'])


if __name__ == '__main__':
    import unittest

    unittest.main()
