import uuid

from ras_party.support.requests_wrapper import Requests

from test.mocks import MockRequests
from test.party_client import PartyTestClient, businesses
from test.test_data.mock_business import MockBusiness


class TestParties(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().attributes(source='test_post_valid_business_adds_to_db').as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

    def test_post_valid_party_adds_to_db(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()
        self.post_to_parties(mock_party, 200)

        self.assertEqual(len(businesses()), 1)

    def test_get_business_by_id_returns_correct_representation(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id)
        self.assertEqual(len(response.items()), 6)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), mock_business['sampleSummaryId'])
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_id_and_collection_exercise_returns_correct_representation(self):
        # Post business and link to sample/collection exercise
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_and_collection_exercise_returns_correct_representation') \
            .as_business()
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
        self.assertEqual(len(response.items()), 6)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), sample_id)
        self.assertEqual(response.get('name'), mock_business.get('name'))

        # Retrieve data for 2nd collection exercise
        response = self.get_business_by_id(party_id, query_string={"collection_exercise_id": "other_test_id"})
        self.assertEqual(len(response.items()), 6)
        self.assertEqual(response.get('id'), party_id)
        self.assertEqual(response.get('sampleSummaryId'), '100000001')
        self.assertEqual(response.get('name'), mock_business.get('name'))

    def test_get_business_by_id_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_id_returns_correct_representation_summary') \
            .as_business()
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id, query_string={"verbose": "true"})
        self.assertTrue(len(response.items()) >= len(mock_business.items()))

    def test_put_business_sample_link_200(self):
        mock_business = MockBusiness().attributes(source='test_put_business_sample_link_200').as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

        sample_id = mock_business['sampleSummaryId']
        put_data = {'collectionExerciseId': 'somecollectionexcid'}

        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_put_business_sample_link_returns_400_when_no_ce(self):
        mock_business = MockBusiness()\
            .attributes(source='test_put_business_sample_link_returns_400_when_no_ce').as_business()
        sample_id = mock_business['sampleSummaryId']
        self.put_to_businesses_sample_link(sample_id, {}, 400)

    def test_get_business_by_ref_returns_correct_representation_verbose(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_ref_returns_correct_representation') \
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['sampleUnitRef'], query_string={"verbose": "true"})

        del mock_business['sampleSummaryId']
        for x in mock_business:
            self.assertIn(x, response)

    def test_get_party_by_id_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_id_returns_correct_representation') \
            .as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        response = self.get_party_by_id('B', party_id_b)

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_get_party_by_id_filtered_by_survey_id_returns_correct_representation(self):
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        associations = [{
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "name": "Business Register and Employment Survey",
                    "surveyId": survey_id
                }
            ],
            "partyId": "7e1e54db-6126-47da-abae-94de5358432a"
        }]
        mock_party_b = MockBusiness() \
            .attributes(associations=associations) \
            .as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        response = self.get_party_by_id_filtered_by_survey('B', party_id_b, survey_id)

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_get_party_filtered_by_survey_filters_with_other_surveys(self):
        survey_id = "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
        associations = [{
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "name": "Business Register and Employment Survey",
                    "surveyId": survey_id
                },
                {
                    "enrolmentStatus": "CREATED",
                    "name": "MBS",
                    "surveyId": "wrong_survey_id"
                }
            ],
            "partyId": "7e1e54db-6126-47da-abae-94de5358432a"
        },
            {
                "enrolments": [
                    {
                        "enrolmentStatus": "CREATED",
                        "name": "MBS",
                        "surveyId": "wrong_survey_id"
                    }
                ],
                "partyId": "7e1e54db-6126-47da-abae-94de5358432b"
            }
        ]
        mock_party_b = MockBusiness() \
            .attributes(associations=associations) \
            .as_party()
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        response = self.get_party_by_id_filtered_by_survey('B', party_id_b, survey_id)

        expected_response = [{
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "name": "Business Register and Employment Survey",
                    "surveyId": survey_id
                }
            ],
            "partyId": "7e1e54db-6126-47da-abae-94de5358432a"
        }
        ]
        self.assertEqual(response['associations'], expected_response)

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness() \
            .attributes(source='test_get_party_by_ref_returns_correct_representation') \
            .as_party()
        self.post_to_parties(mock_party_b, 200)
        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])

        del mock_party_b['sampleSummaryId']
        for x in mock_party_b:
            self.assertTrue(x in response)

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness() \
            .attributes(source='test_existing_business_can_be_updated', version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)

        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['version'], 2)

    def test_existing_party_can_be_updated(self):
        mock_party = MockBusiness() \
            .attributes(source='test_existing_party_can_be_updated', version=1)

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
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()
        del mock_party['sampleUnitRef']
        self.post_to_parties(mock_party, 400)

    def test_get_party_with_invalid_unit_type(self):
        self.get_party_by_id('XX', '123', 400)
        self.get_party_by_ref('XX', '123', 400)

    def test_get_party_with_nonexistent_ref(self):
        self.get_party_by_ref('B', '123', 404)


if __name__ == '__main__':
    import unittest

    unittest.main()
