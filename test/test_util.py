from unittest import TestCase

from ras_party.support.util import flatten_keys, obfuscate_email


class TestUtil(TestCase):
    def test_flatten_keys_produces_expected_results(self):
        d = {"name": "Foo", "other": {"name": "Bar"}}

        actual = flatten_keys(d)

        expected = ["name", "other", "other.name"]

        self.assertCountEqual(actual, expected)

    def test_obfuscate_email(self):
        """Test obfuscate_email correctly changes inputted emails"""

        testAddresses = {
            "example@example.com": "e*****e@e*********m",
            "prefix@domain.co.uk": "p****x@d**********k",
            "first.name@place.gov.uk": "f********e@p**********k",
            "me+addition@gmail.com": "m*********n@g*******m",
            "a.b.c.someone@example.com": "a***********e@e*********m",
            "john.smith123456@londinium.ac.co.uk": "j**************6@l****************k",
            "me!?@example.com": "m**?@e*********m",
            "m@m.com": "m@m***m",
            "joe.bloggs": "j********s",
            "joe.bloggs@": "j********s",
            "@gmail.com": "@g*******m",
        }

        for test in testAddresses:
            self.assertEqual(obfuscate_email(test), testAddresses[test])
