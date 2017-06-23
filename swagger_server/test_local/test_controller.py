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
        party_id = self.post_to_businesses(mock_business, 200)['id']

        response = self.get_business_by_id(party_id)
        self.assertTrue(response.items() >= mock_business.items())

    def test_get_business_by_ref_returns_correct_representation(self):
        mock_business = MockBusiness()\
            .attributes(source='test_get_business_by_ref_returns_correct_representation')\
            .as_business()
        self.post_to_businesses(mock_business, 200)

        response = self.get_business_by_ref(mock_business['businessRef'])
        self.assertTrue(response.items() >= mock_business.items())

    def test_post_valid_respondent_adds_to_db(self):
        mock_respondent = MockRespondent().attributes().as_respondent()

        self.post_to_respondents(mock_respondent, 200)

        self.assertEqual(len(respondents()), 1)

    def test_get_respondent_by_id_returns_correct_representation(self):
        mock_respondent = MockRespondent().attributes().as_respondent()
        party_id = self.post_to_respondents(mock_respondent, 200)['id']

        response = self.get_respondent_by_id(party_id)
        self.assertTrue(response.items() >= mock_respondent.items())

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
        party_id_b = self.post_to_parties(mock_party_b, 200)['id']

        mock_party_bi = MockRespondent().attributes().as_party()
        party_id_bi = self.post_to_parties(mock_party_bi, 200)['id']

        response = self.get_party_by_id('B', party_id_b)
        self.assertTrue(response.items() >= mock_party_b.items())

        response = self.get_party_by_id('BI', party_id_bi)
        self.assertTrue(response.items() >= mock_party_bi.items())

    def test_get_party_by_ref_returns_correct_representation(self):
        mock_party_b = MockBusiness()\
            .attributes(source='test_get_party_by_ref_returns_correct_representation')\
            .as_party()
        self.post_to_parties(mock_party_b, 200)

        response = self.get_party_by_ref('B', mock_party_b['sampleUnitRef'])
        self.assertTrue(response.items() >= mock_party_b.items())

    def test_existing_business_can_be_updated(self):
        mock_business = MockBusiness()\
            .attributes(source='test_existing_business_can_be_updated', version=1)
        response_1 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_business.attributes(version=2)
        response_2 = self.post_to_businesses(mock_business.as_business(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)

    def test_existing_respondent_can_be_updated(self):
        # TODO: clarify the PK on which an update would be done
        pass

    def test_existing_party_can_be_updated(self):
        mock_party = MockBusiness()\
            .attributes(source='test_existing_respondent_can_be_updated', version=1)

        response_1 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_1['attributes']['version'], 1)

        mock_party.attributes(version=2)
        response_2 = self.post_to_parties(mock_party.as_party(), 200)
        self.assertEqual(len(businesses()), 1)
        self.assertEqual(response_2['attributes']['version'], 2)


if __name__ == '__main__':
    import unittest

    unittest.main()
