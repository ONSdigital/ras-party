import json
from test.party_client import PartyTestClient


class TestParties(PartyTestClient):
    def test_info_endpoint(self):
        response = self.client.open("/info", method="GET")
        response_data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response_data)
        self.assertIn("version", response_data)


if __name__ == "__main__":
    import unittest

    unittest.main()
