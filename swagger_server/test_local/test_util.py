from unittest import TestCase

from swagger_server.controllers_local.util import flatten_keys
import collections

class TestUtil(TestCase):

    def test_flatten_keys_produces_expected_results(self):
        d = {
            "name": "Foo",
            "other": {
                "name": "Bar"
            }
        }

        actual = flatten_keys(d)

        expected = ['name', 'other', 'other.name']

        #self.assertEqual(actual, expected)

        # Flatten doesn't guarantee order in resulting list ..
        self.assertTrue(collections.Counter(actual) == collections.Counter(expected))
