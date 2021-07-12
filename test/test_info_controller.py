from test.party_client import PartyTestClient


class TestParties(PartyTestClient):
    def test_info_endpoint(self):
        response = self.get_info()
        self.assertIn("name", response)
        self.assertIn("version", response)


if __name__ == "__main__":
    import unittest

    unittest.main()
