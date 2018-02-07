from ras_party.support.requests_wrapper import Requests

from test.mocks import MockRequests
from test.party_client import PartyTestClient
from test.test_data.mock_business import MockBusiness


class TestBusinessesSearch(PartyTestClient):

    def setUp(self):
        self.mock_requests = MockRequests()
        Requests._lib = self.mock_requests

    def test_get_business_by_search_ru(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_ru') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)

        # when user searches by ru
        response = self.get_businesses_search(query_string={"query": business['ruref']})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['ruref'])

    def test_get_business_by_search_name(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)

        # when user searches by name
        response = self.get_businesses_search(query_string={"query": business['name']})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['ruref'])
        self.assertEqual(response[0]['name'], business['name'])

    def test_get_business_by_search_partial_ru(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_ru') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)

        # when user searches by partial ru
        response = self.get_businesses_search(query_string={"query": business['ruref'][4:]})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['ruref'])

    def test_get_business_by_search_partial_name(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_name') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": business['name'][5:]})

        # then th correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['ruref'])
        self.assertEqual(response[0]['name'], business['name'])

    def test_get_business_by_search_prefix_ru(self):
        mock_business = MockBusiness() \
            .attributes(source='test_get_business_by_search_partial_ru') \
            .as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)

        # when user searches by ru with ru prefix
        response = self.get_businesses_search(query_string={"query": f"ru{business['ruref'][4:]}"})

        # then the correct business is returned
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['ruref'], business['ruref'])

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

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": mock_business['runame1']})

        # then distinct variations of the correct business is returned
        self.assertEqual(len(response), 3)
        self.assertEqual(name_1, response[0]['name'])
        self.assertEqual(name_2, response[1]['name'])
        self.assertEqual(name_3, response[2]['name'])
