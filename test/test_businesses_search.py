from ras_party.support.requests_wrapper import Requests

from test.mocks import MockRequests
from test.party_client import PartyTestClient
from test.test_data.mock_business import MockBusiness


class TestBusinessesSearch(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

    def _make_business_attributes_active(self, mock_business):
        sample_id = mock_business['sampleSummaryId']
        put_data = {'collectionExerciseId': 'test_id'}
        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_get_business_by_search_ru(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_ru') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by ru
        response = self.get_businesses_search(query_string={"query": business['sampleUnitRef']})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])

    def test_get_business_by_search_name(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by name
        response = self.get_businesses_search(query_string={"query": business['name']})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])
        self.assertEqual(response[0]['name'], business['name'])
        self.assertEqual(response[0]['trading_as'], business['trading_as'])

    def test_get_business_by_search_trading_as(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by name
        response = self.get_businesses_search(query_string={"query": business['trading_as']})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])
        self.assertEqual(response[0]['name'], business['name'])
        self.assertEqual(response[0]['trading_as'], business['trading_as'])

    def test_get_business_by_search_partial_ru(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_ru') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by partial ru
        response = self.get_businesses_search(query_string={"query": business['sampleUnitRef'][4:]})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])

    def test_get_business_by_search_partial_name(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": business['name'][5:]})

        # then th correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])
        self.assertEqual(response[0]['name'], business['name'])
        self.assertEqual(response[0]['trading_as'], business['trading_as'])

    def test_get_business_by_search_key_words_in_name(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_key_words_in_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by multiple key words in name
        response = self.get_businesses_search(query_string={"query": f"{business['attributes']['runame1']}"
                                                                     f" {business['attributes']['runame3']}"})

        # then th correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['sampleUnitRef'])
        self.assertEqual(response[0]['name'], business['name'])
        self.assertEqual(response[0]['trading_as'], business['trading_as'])

    def test_get_business_by_search_distinct_multi_names(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_ru') \
            .as_business()

        # given there is a business with multiple names to search
        self.post_to_businesses(mock_business, 200)
        name_1 = self.post_to_businesses(mock_business, 200)['name']
        mock_business['runame2'] = 'another1'
        name_2 = self.post_to_businesses(mock_business, 200)['name']
        mock_business['runame3'] = 'another1'
        name_3 = self.post_to_businesses(mock_business, 200)['name']
        self._make_business_attributes_active(mock_business)

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": mock_business['runame1']})

        # then distinct variations of the correct business is returned
        names = [business['name'] for business in response]
        self.assertEqual(len(response), 3)
        self.assertIn(name_1, names)
        self.assertIn(name_2, names)
        self.assertIn(name_3, names)

    def test_get_business_by_search_inactive_business_attributes(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_ru') \
            .as_business()

        # given there is a business but it's attributes are not linked to a collection exercise (inactive)
        name = self.post_to_businesses(mock_business, 200)['name']

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": name})

        # then no businesses returned
        self.assertEqual(len(response), 0)
