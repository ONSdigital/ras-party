from flask import current_app
from flask_testing import TestCase

from ras_party.support.public_website import PublicWebsite
from run import create_app


class TestPublicWebsite(TestCase):

    def create_app(self):
        return create_app('TestingConfig')

    def test_reset_password_url_includes_standard_port_for_http(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'http://mockhost:80'

        unit = PublicWebsite()

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "http://mockhost:80/passwords/reset-password/"
        # TODO: ought to be possible to mock the token generator, so we can predict the entire url
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_includes_nonstandard_port_for_http(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'http://mockhost:1234'

        unit = PublicWebsite()

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "http://mockhost:1234/passwords/reset-password/"
        # TODO: ought to be possible to mock the token generator, so we can predict the entire url
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_includes_standard_port_for_https(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'https://mockhost:443'

        unit = PublicWebsite()

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "https://mockhost:443/passwords/reset-password/"
        # TODO: ought to be possible to mock the token generator, so we can predict the entire url
        self.assertIn(expected_url_substring, actual_url)

    def test_reset_password_url_includes_port_80_when_scheme_is_https(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'https://mockhost:80'

        unit = PublicWebsite()

        # When the reset password url is constructed
        actual_url = unit.reset_password_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "https://mockhost:80/passwords/reset-password/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_includes_nonstandard_port_for_http(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'http://mockhost:1234'

        unit = PublicWebsite()

        # When the activate account url is constructed
        actual_url = unit.activate_account_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "http://mockhost:1234/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)

    def test_activate_account_url_includes_port_80_when_scheme_is_https(self):
        current_app.config['RAS_PUBLIC_WEBSITE_URL'] = 'https://mockhost:80'

        unit = PublicWebsite()

        actual_url = unit.activate_account_url('test@email.com')

        # Then it contains the port number
        expected_url_substring = "https://mockhost:80/register/activate-account/"
        self.assertIn(expected_url_substring, actual_url)
