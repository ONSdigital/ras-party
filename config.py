# flake8: noqa
import os

from ras_party.cloud.cloudfoundry import ONSCloudFoundry


cf = ONSCloudFoundry()


def _is_true(value):
    try:
        return value.lower() in ('true', 't', 'yes', 'y', '1')
    except AttributeError:
        return value is True


class Config(object):

    NAME = os.getenv('RAS-PARTY', 'ras-party')
    VERSION = os.getenv('VERSION', '1.2.2')
    SCHEME = os.getenv('http')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8081)
    DEBUG = _is_true(os.getenv('DEBUG', False))
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    SECRET_KEY = os.getenv('SECRET_KEY', 'aardvark')
    EMAIL_TOKEN_SALT = os.getenv('EMAIL_TOKEN_SALT', 'aardvark')
    EMAIL_TOKEN_EXPIRY = int(os.getenv('EMAIL_TOKEN_EXPIRY', 306000))
    PARTY_SCHEMA = os.getenv('PARTY_SCHEMA', 'ras_party/schemas/party_schema.json')

    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 5))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 10))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', -1))

    if cf.detected:
        DATABASE_SCHEMA = 'partysvc'
        DATABASE_URI = cf.db.credentials['uri']
    else:
        DATABASE_SCHEMA = os.getenv('DATABASE_SCHEMA', 'partysvc')
        DATABASE_URI = os.getenv('DATABASE_URI', "postgres://postgres:postgres@localhost:5432/postgres")

    REQUESTS_GET_TIMEOUT = os.getenv('REQUESTS_GET_TIMEOUT', 20)
    REQUESTS_POST_TIMEOUT = os.getenv('REQUESTS_POST_TIMEOUT', 20)
    SECURITY_USER_NAME = os.getenv('SECURITY_USER_NAME', 'admin')
    SECURITY_USER_PASSWORD = os.getenv('SECURITY_USER_PASSWORD', 'secret')
    SECURITY_REALM = os.getenv('SECURITY_REALM', 'sdc')

    # dependencies

    RAS_PUBLIC_WEBSITE_PROTOCOL = os.getenv('RAS_PUBLIC_WEBSITE_PROTOCOL', 'http')
    RAS_PUBLIC_WEBSITE_HOST = os.getenv('RAS_PUBLIC_WEBSITE_HOST', 'localhost')
    RAS_PUBLIC_WEBSITE_PORT = os.getenv('RAS_PUBLIC_WEBSITE_PORT', 8082)
    RAS_PUBLIC_WEBSITE_URL = f'{RAS_PUBLIC_WEBSITE_PROTOCOL}://{RAS_PUBLIC_WEBSITE_HOST}:{RAS_PUBLIC_WEBSITE_PORT}'

    RAS_CASE_SERVICE_PROTOCOL = os.getenv('RAS_CASE_SERVICE_PROTOCOL', 'http')
    RAS_CASE_SERVICE_HOST = os.getenv('RAS_CASE_SERVICE_HOST', 'localhost')
    RAS_CASE_SERVICE_PORT = os.getenv('RAS_CASE_SERVICE_PORT', 8171)
    RAS_CASE_SERVICE = f'{RAS_CASE_SERVICE_PROTOCOL}://{RAS_CASE_SERVICE_HOST}:{RAS_CASE_SERVICE_PORT}'

    RAS_COLLEX_SERVICE_PROTOCOL = os.getenv('RAS_COLLEX_SERVICE_PROTOCOL', 'http')
    RAS_COLLEX_SERVICE_HOST = os.getenv('RAS_COLLEX_SERVICE_HOST', 'localhost')
    RAS_COLLEX_SERVICE_PORT = os.getenv('RAS_COLLEX_SERVICE_PORT', 8145)
    RAS_COLLEX_SERVICE = f'{RAS_COLLEX_SERVICE_PROTOCOL}://{RAS_COLLEX_SERVICE_HOST}:{RAS_COLLEX_SERVICE_PORT}'

    RAS_SURVEY_SERVICE_PROTOCOL = os.getenv('RAS_SURVEY_SERVICE_PROTOCOL', 'http')
    RAS_SURVEY_SERVICE_HOST = os.getenv('RAS_SURVEY_SERVICE_HOST', 'localhost')
    RAS_SURVEY_SERVICE_PORT = os.getenv('RAS_SURVEY_SERVICE_PORT', 8080)
    RAS_SURVEY_SERVICE = f'{RAS_SURVEY_SERVICE_PROTOCOL}://{RAS_SURVEY_SERVICE_HOST}:{RAS_SURVEY_SERVICE_PORT}'

    RAS_NOTIFY_SERVICE_URL = os.getenv('RAS_NOTIFY_SERVICE_URL', 'http://notify-gateway-service/emails/')
    RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE = os.getenv('RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE', 'email_verification_id')
    RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = os.getenv('RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE', 'request_password_change_id')
    RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = os.getenv('RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE', 'confirm_password_change_id')

    RAS_API_GATEWAY_PROTOCOL = os.getenv('RAS_API_GATEWAY_PROTOCOL', 'http')
    RAS_API_GATEWAY_HOST = os.getenv('RAS_API_GATEWAY_HOST', 'localhost')
    RAS_API_GATEWAY_PORT = os.getenv('RAS_API_GATEWAY_PORT', 8083)
    RAS_API_GATEWAY = f'{RAS_API_GATEWAY_PROTOCOL}://{RAS_API_GATEWAY_HOST}:{RAS_API_GATEWAY_PORT}'

    RAS_IAC_SERVICE_PROTOCOL = os.getenv('RAS_IAC_SERVICE_PROTOCOL', 'http')
    RAS_IAC_SERVICE_HOST = os.getenv('RAS_IAC_SERVICE_HOST', 'localhost')
    RAS_IAC_SERVICE_PORT = os.getenv('RAS_IAC_SERVICE_PORT', 8121)
    RAS_IAC_SERVICE = f'{RAS_IAC_SERVICE_PROTOCOL}://{RAS_IAC_SERVICE_HOST}:{RAS_IAC_SERVICE_PORT}'

    RAS_OAUTH_SERVICE_PROTOCOL = os.getenv('RAS_OAUTH_SERVICE_PROTOCOL', 'http')
    RAS_OAUTH_SERVICE_HOST = os.getenv('RAS_OAUTH_SERVICE_HOST', 'localhost')
    RAS_OAUTH_SERVICE_PORT = os.getenv('RAS_OAUTH_SERVICE_PORT', 8040)
    RAS_OAUTH_SERVICE = f'{RAS_OAUTH_SERVICE_PROTOCOL}://{RAS_OAUTH_SERVICE_HOST}:{RAS_OAUTH_SERVICE_PORT}'
    RAS_OAUTH_CLIENT_ID = os.getenv('RAS_OAUTH_CLIENT_ID', 'ons@ons.gov')
    RAS_OAUTH_CLIENT_SECRET = os.getenv('RAS_OAUTH_CLIENT_SECRET', 'password')

    DEPENDENCIES = [
        'ras-party-db',
        'public-website',
        'case-service',
        'collectionexercise-service',
        'survey-service',
        'notify-service',
        'api-gateway',
        'iac-service',
        'oauth2-service',
    ]

    # features

    REPORT_DEPENDENCIES = _is_true(os.getenv('REPORT_DEPENDENCIES', False))
    SEND_EMAIL_TO_GOV_NOTIFY = _is_true(os.getenv('SEND_EMAIL_TO_GOV_NOTIFY', False))


class DevelopmentConfig(Config):

    DEBUG = True
    LOGGING_LEVEL = 'DEBUG'


class TestingConfig(DevelopmentConfig):

    DEBUG = True
    LOGGING_LEVEL = 'ERROR'
    SECRET_KEY = 'aardvark'
    EMAIL_TOKEN_SALT = 'bulbous'
    PARTY_SCHEMA = 'ras_party/schemas/party_schema.json'
    SECURITY_USER_NAME = 'username'
    SECURITY_USER_PASSWORD = 'password'
    REQUESTS_GET_TIMEOUT = 99
    REQUESTS_POST_TIMEOUT = 99
    DATABASE_SCHEMA = 'partysvc'

    RAS_PUBLIC_WEBSITE_URL = 'http://dummy.ons.gov.uk'
    RAS_CASE_SERVICE = 'http://mockhost:1111'
    RAS_COLLEX_SERVICE = 'http://mockhost:2222'
    RAS_SURVEY_SERVICE = 'http://mockhost:3333'
    RAS_OAUTH_SERVICE = 'http://mockhost:4444'
    RAS_OAUTH_CLIENT_ID = 'ons@ons.gov'
    RAS_OAUTH_CLIENT_SECRET = 'password'
    RAS_NOTIFY_SERVICE_URL = 'http://notifygatewaysvc-dev.apps.devtest.onsclofo.uk/emails/'
    RAS_NOTIFY_EMAIL_VERIFICATION_TEMPLATE = 'email_verification_id'
    RAS_NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = 'request_password_change_id'
    RAS_NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = 'confirm_password_change_id'
    RAS_IAC_SERVICE = 'http://mockhost:6666'

    SEND_EMAIL_TO_GOV_NOTIFY = True
