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

    def test_reset_password_url_includes_nonstandard_port_for_http(self):
        # Given config contains SCHEME 'http and PORT 1234
        config = MockConfig(scheme='http', port=1234)
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "http://mockhost:1234/passwords/reset-password/"
        # TODO: ought to be possible to mock the token generator, so we can predict the entire url
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_excludes_int_port_80_when_scheme_is_http(self):
        # Given config contains SCHEME 'http' and PORT 80
        config = MockConfig(scheme='http', port=80)
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        expected_url_substring = "http://mockhost/passwords/reset-password/"
        # Then it does not contain the port number
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_excludes_string_port_80_when_scheme_is_http(self):
        # Given config contains SCHEME 'http' and PORT '80' (in string format)
        config = MockConfig(port='80')
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "http://mockhost/passwords/reset-password/"
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_excludes_int_port_443_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT 443
        config = MockConfig(scheme='https', port=443)
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "https://mockhost/passwords/reset-password/"
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_excludes_string_port_443_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT '443' (in string format)
        config = MockConfig(scheme='https', port='443')
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "https://mockhost/passwords/reset-password/"
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_includes_port_80_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT 80
        config = MockConfig(scheme='https', port=80)
        unit = PublicWebsite(config)

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "https://mockhost:80/passwords/reset-password/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_includes_nonstandard_port_for_http(self):
        # Given config contains SCHEME 'http' and PORT 1234
        config = MockConfig(scheme='http', port=1234)
        unit = PublicWebsite(config)

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "http://mockhost:1234/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_excludes_int_port_80_when_scheme_is_http(self):
        # Given config contains SCHEME 'http' and PORT 80
        config = MockConfig(scheme='http', port=80)
        unit = PublicWebsite(config)

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "http://mockhost/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_excludes_string_port_80_when_scheme_is_http(self):
        # Given config contains SCHEME 'http' and PORT '80' (in string format)
        config = MockConfig(scheme='http', port='80')
        unit = PublicWebsite(config)

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "http://mockhost/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_excludes_int_port_443_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT 443
        config = MockConfig(scheme='https', port=443)
        unit = PublicWebsite(config)

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "https://mockhost/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_excludes_string_port_443_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT '443' (in string format)
        config = MockConfig(scheme='https', port='443')
        unit = PublicWebsite(config)

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it does not contain the port number
        expected_url_substring = "https://mockhost/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_includes_port_80_when_scheme_is_https(self):
        # Given config contains SCHEME 'https' and PORT 80
        config = MockConfig(scheme='https', port=80)
        unit = PublicWebsite(config)

        actual_url = unit.activate_account_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "https://mockhost:80/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)
