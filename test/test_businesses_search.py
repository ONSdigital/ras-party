import copy
from test.party_client import PartyTestClient
from test.test_data.mock_business import DEFAULT_ATTRIBUTES, MockBusiness


class TestBusinessesSearch(PartyTestClient):
    def _make_business_attributes_active(self, mock_business):
        sample_id = mock_business["sampleSummaryId"]
        put_data = {"collectionExerciseId": "test_id"}
        self.put_to_businesses_sample_link(sample_id, put_data, 200)

    def test_get_business_by_search_ru(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by ru
        response = self.get_businesses_search(query_string={"query": business["sampleUnitRef"]})

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])

    def test_get_business_by_search_name(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by name
        response = self.get_businesses_search(query_string={"query": business["name"]})

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])
        self.assertEqual(response["businesses"][0]["name"], business["name"])
        self.assertEqual(response["businesses"][0]["trading_as"], business["trading_as"])

    def test_get_business_by_search_trading_as(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by name
        response = self.get_businesses_search(query_string={"query": business["trading_as"]})

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])
        self.assertEqual(response["businesses"][0]["name"], business["name"])
        self.assertEqual(response["businesses"][0]["trading_as"], business["trading_as"])

    def test_get_business_by_search_partial_ru(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by partial ru
        response = self.get_businesses_search(query_string={"query": business["sampleUnitRef"][4:]})

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])

    def test_get_business_by_search_partial_name(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": business["name"][5:]})

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])
        self.assertEqual(response["businesses"][0]["name"], business["name"])
        self.assertEqual(response["businesses"][0]["trading_as"], business["trading_as"])

    def test_get_business_by_search_key_words_in_name(self):
        mock_business = MockBusiness().as_business()

        # given there is a business to search
        business = self.post_to_businesses(mock_business, 200)
        self._make_business_attributes_active(mock_business)

        # when user searches by multiple keywords in name
        response = self.get_businesses_search(
            query_string={"query": f"{business['attributes']['runame1']}" f" {business['attributes']['runame3']}"}
        )

        # then the correct business is returned
        self.assertEqual(len(response["businesses"]), 1)
        self.assertEqual(response["businesses"][0]["ruref"], business["sampleUnitRef"])
        self.assertEqual(response["businesses"][0]["name"], business["name"])
        self.assertEqual(response["businesses"][0]["trading_as"], business["trading_as"])

    def test_get_business_by_search_distinct_multi_names(self):
        mock_business = MockBusiness().as_business()

        # given there is a business with multiple names to search
        self.post_to_businesses(mock_business, 200)
        name_1 = self.post_to_businesses(mock_business, 200)["name"]
        mock_business["runame2"] = "another1"
        name_2 = self.post_to_businesses(mock_business, 200)["name"]
        mock_business["runame3"] = "another1"
        name_3 = self.post_to_businesses(mock_business, 200)["name"]
        self._make_business_attributes_active(mock_business)

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": mock_business["runame1"]})

        # then distinct variations of the correct business is returned
        names = [business["name"] for business in response["businesses"]]
        self.assertEqual(len(response["businesses"]), 3)
        self.assertIn(name_1, names)
        self.assertIn(name_2, names)
        self.assertIn(name_3, names)

    def test_business_search_gives_correct_number_per_page(self):
        setup_count = 20
        self._set_up_businesses(count=setup_count)
        for limit in [2, 10, 15, 20]:
            with self.subTest(limit=limit):
                response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=1, limit=limit)
                self.assertEqual(len(response["businesses"]), limit)
                self.assertEqual(response["total_business_count"], setup_count)

    def test_business_search_gets_correct_page_and_ordered_by_name(self):
        self._set_up_businesses(count=10)

        response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=2, limit=5)
        self.assertIn("5-", response["businesses"][0]["name"])
        self.assertIn("6-", response["businesses"][1]["name"])
        self.assertIn("7-", response["businesses"][2]["name"])
        self.assertIn("8-", response["businesses"][3]["name"])
        self.assertIn("9-", response["businesses"][4]["name"])

    def test_business_search_gets_partial_page_if_result_count_less_than_limit(self):
        self._set_up_businesses(count=5)

        response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=1, limit=10)
        self.assertEqual(len(response["businesses"]), 5)

    def test_business_search_returns_partial_page_if_last_page_not_full(self):
        setup_count = 25
        self._set_up_businesses(count=setup_count)

        response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=3, limit=10)
        self.assertEqual(len(response["businesses"]), 5)
        self.assertEqual(response["total_business_count"], setup_count)

    def test_business_search_returns_empty_list_if_no_results(self):
        response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=3, limit=10)
        self.assertEqual(len(response["businesses"]), 0)

    def test_business_search_returns_empty_list_if_page_too_high(self):
        self._set_up_businesses(count=10)

        response = self.get_businesses_search(200, query_string={"query": "Runame-1"}, page=3, limit=10)
        self.assertEqual(len(response["businesses"]), 0)

    def test_business_search_with_no_pagination_parameters_uses_default_params(self):
        expected_count = 111
        self._set_up_businesses(count=expected_count)
        response = self.get_businesses_search(200, query_string={"query": "Runame-1"})
        self.assertEqual(len(response["businesses"]), 100)
        self.assertEqual(expected_count, response["total_business_count"])

    def test_get_business_by_search_inactive_business_attributes(self):
        mock_business = MockBusiness().as_business()

        # given there is a business but its attributes are not linked to a collection exercise (inactive)
        name = self.post_to_businesses(mock_business, 200)["name"]

        # when user searches by partial name
        response = self.get_businesses_search(query_string={"query": name})

        # then no businesses returned
        self.assertEqual(len(response["businesses"]), 0)

    def _set_up_businesses(self, count):
        """set up multiple businesses with unique ru refs and names and trading as starting in <n>-"""
        for i in range(count):
            attribs = copy.deepcopy(DEFAULT_ATTRIBUTES)
            attribs["runame1"] = f"{i}-Runame-1"
            attribs["runame2"] = f"{i}-Runame-2"
            attribs["runame3"] = f"{i}-Runame-3"
            attribs["name"] = f'{attribs["runame1"]} {attribs["runame2"]} {attribs["runame3"]}'

            attribs["tradstyle1"] = f"{i}-Tradstyle-1"
            attribs["tradstyle2"] = f"{i}-Tradstyle-2"
            attribs["tradstyle3"] = f"{i}-Tradstyle-3"
            attribs["trading_as"] = f'{attribs["tradstyle1"]} {attribs["tradstyle2"]} {attribs["tradstyle3"]}'

            mock_business = MockBusiness(attribs).as_business()

            self.post_to_businesses(mock_business, 200)
            self._make_business_attributes_active(mock_business)
