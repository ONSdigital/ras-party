from __future__ import absolute_import

from swagger_server.test_local.mocks import MockBusiness, MockRespondent
from swagger_server.test_local.party_client import PartyTestClient, businesses, respondents


class TestParties(PartyTestClient):

    def test_post_valid_business_adds_to_db(self):
        mock_business = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_business()
        self.post_to_businesses(mock_business, 200)

        self.assertEqual(len(businesses()), 1)

    def test_get_business_by_id_returns_correct_representation(self):
        mock_business = MockBusiness()\
            .attributes(source='test_get_business_by_id_returns_correct_representation')\
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_id(mock_business['id'])
        self.assertEqual(response, mock_business)

    def test_get_business_by_ref_returns_correct_representation(self):
        mock_business = MockBusiness()\
            .attributes(source='test_get_business_by_ref_returns_correct_representation')\
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['businessRef'])
        self.assertEqual(response, mock_business)

    def test_post_valid_respondent_adds_to_db(self):
        mock_respondent = MockRespondent().attributes().as_respondent()

        self.post_to_respondents(mock_respondent, 200)

        self.assertEqual(len(respondents()), 1)

    def test_get_respondent_by_id_returns_correct_representation(self):
        mock_respondent = MockRespondent().attributes().as_respondent()
        self.post_to_respondents(mock_respondent, 200)

        response = self.get_respondent_by_id(mock_respondent['id'])
        self.assertEqual(response, mock_respondent)

    def test_post_valid_party_adds_to_db(self):
        mock_party = MockBusiness().attributes(source='test_post_valid_party_adds_to_db').as_party()

        self.post_to_parties(mock_party, 200)
        self.assertEqual(len(businesses()), 1)

        mock_party = MockRespondent().attributes().as_respondent()

        self.post_to_parties(mock_party, 200)
        self.assertEqual(len(businesses()), 1)

    def test_get_party_by_id_returns_correct_representation(self):
        mock_party_b = MockBusiness()\
            .attributes(source='test_get_party_by_id_returns_correct_representation')\
            .as_party()
        self.post_to_parties(mock_party_b, 200)

        mock_party_bi = MockRespondent().attributes().as_party()
        self.post_to_parties(mock_party_bi, 200)

        response = self.get_party_by_id('B', mock_party_b['id'])
        self.assertEqual(response, mock_party_b)

        response = self.get_party_by_id('BI', mock_party_bi['id'])
        self.assertEqual(response, mock_party_bi)

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness()\
            .attributes(source='test_get_party_by_ref_returns_correct_representation')\
            .as_party()
        self.post_to_parties(mock_party_b, 200)

        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])
        self.assertEqual(response, mock_party_b)


if __name__ == '__main__':
    import unittest

    unittest.main()
