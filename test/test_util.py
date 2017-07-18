from unittest import TestCase

from ras_party.controllers.util import flatten_keys


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

        self.assertCountEqual(actual, expected)
