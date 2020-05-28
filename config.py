# flake8: noqa
import os
from distutils.util import strtobool


def _is_true(value):
    try:
        return value.lower() in ('true', 't', 'yes', 'y', '1')
    except AttributeError:
        return value is True


class Config(object):
    VERSION = '1.13.0'
    SCHEME = os.getenv('http')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8081)
    DEBUG = _is_true(os.getenv('DEBUG', False))
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    SECRET_KEY = os.getenv('SECRET_KEY', 'aardvark')
    EMAIL_TOKEN_SALT = os.getenv('EMAIL_TOKEN_SALT', 'aardvark')
    EMAIL_TOKEN_EXPIRY = int(os.getenv('EMAIL_TOKEN_EXPIRY', '306000'))
    PARTY_SCHEMA = os.getenv('PARTY_SCHEMA', 'ras_party/schemas/party_schema.json')

    DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA', 'partysvc')
    DATABASE_URI = os.getenv('DATABASE_URI', "postgresql://postgres:postgres@localhost:5432/postgres")

    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')

    # dependencies
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL')
    CASE_SERVICE_URL = os.getenv('CASE_SERVICE_URL')
    COLLECTION_EXERCISE_SERVICE_URL = os.getenv('COLLECTION_EXERCISE_SERVICE_URL')
    FRONTSTAGE_URL = os.getenv('FRONTSTAGE_URL')
    IAC_SERVICE_URL = os.getenv('IAC_SERVICE_URL')
    SURVEY_SERVICE_URL = os.getenv('SURVEY_SERVICE_URL')

    NOTIFY_SERVICE_URL = os.getenv('NOTIFY_SERVICE_URL', 'http://notify-gateway-service/emails/')
    NOTIFY_EMAIL_VERIFICATION_TEMPLATE = os.getenv('NOTIFY_EMAIL_VERIFICATION_TEMPLATE', 'email_verification_id')
    NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = os.getenv('NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE',
                                                            'request_password_change_id')
    NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = os.getenv('NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE',
                                                            'confirm_password_change_id')
    NOTIFY_ACCOUNT_LOCKED_TEMPLATE = os.getenv('NOTIFY_ACCOUNT_LOCKED_TEMPLATE', 'account_locked_id')
    SEND_EMAIL_TO_GOV_NOTIFY = _is_true(os.getenv('SEND_EMAIL_TO_GOV_NOTIFY', False))


class DevelopmentConfig(Config):

    DEBUG = True
    LOGGING_LEVEL = 'DEBUG'


class TestingConfig(DevelopmentConfig):

    DEBUG = True
    LOGGING_LEVEL = 'ERROR'
    SECRET_KEY = 'aardvark'
    PARTY_SCHEMA = 'ras_party/schemas/party_schema.json'
    SECURITY_USER_NAME = 'username'
    SECURITY_USER_PASSWORD = 'password'
    DATABASE_SCHEMA = 'partysvc'

    FRONTSTAGE_URL = 'http://dummy.ons.gov.uk'
    CASE_SERVICE_URL = 'http://mockhost:1111'
    COLLECTION_EXERCISE_SERVICE_URL = 'http://mockhost:2222'
    SURVEY_SERVICE_URL = 'http://mockhost:3333'
    AUTH_SERVICE_URL = 'http://mockhost:4444'
    NOTIFY_SERVICE_URL = 'http://mockhost:5555/emails/'
    NOTIFY_EMAIL_VERIFICATION_TEMPLATE = 'email_verification_id'
    NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = 'request_password_change_id'
    NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = 'confirm_password_change_id'
    NOTIFY_ACCOUNT_LOCKED_TEMPLATE = 'account_locked_id'
    IAC_SERVICE_URL = 'http://mockhost:6666'

    SEND_EMAIL_TO_GOV_NOTIFY = True
