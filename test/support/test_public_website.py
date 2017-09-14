from unittest import TestCase

from ras_party.support.public_website import PublicWebsite


class MockConfig:

    def __init__(self, scheme=None, host=None, port=None):
        self.dependency = {
            'public-website': {
                'scheme': scheme or 'http',
                'host': host or 'mockhost',
                'port': port or '1234'
            }
        }

    def __getitem__(self, item):
        return {
            'SECRET_KEY': 'secret',
            'EMAIL_TOKEN_SALT': 'salt'
        }[item]


class TestPublicWebsite(TestCase):

    def test_reset_password_url(self):

        config = MockConfig()
        unit = PublicWebsite(config)

        expected_url_substring = "http://mockhost:1234/passwords/reset-password/"
        actual_url = unit.reset_password_url('test@email.com')

        # TODO: ought to be possible to mock the token generator, so we can predict the entire url
        self.assertIn(expected_url_substring, actual_url)

        config = MockConfig(port=80)
        unit = PublicWebsite(config)

        expected_url_substring = "http://mockhost/passwords/reset-password/"
        actual_url = unit.reset_password_url('test@email.com')

        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url(self):

        config = MockConfig()
        unit = PublicWebsite(config)

        expected_url_substring = "http://mockhost:1234/register/activate-account/"
        actual_url = unit.activate_account_url('test@email.com')

        self.assertIn(expected_url_substring, actual_url)

        config = MockConfig(port=80)
        unit = PublicWebsite(config)

        expected_url_substring = "http://mockhost/register/activate-account/"
        actual_url = unit.activate_account_url('test@email.com')

        self.assertIn(expected_url_substring, actual_url)
