# flake8: noqa
import os
from distutils.util import strtobool


def _is_true(value):
    try:
        return value.lower() in ("true", "t", "yes", "y", "1")
    except AttributeError:
        return value is True


class Config(object):
    VERSION = "1.13.0"
    SCHEME = os.getenv("http")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = os.getenv("PORT", 8081)
    DEBUG = _is_true(os.getenv("DEBUG", False))
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
    SECRET_KEY = os.getenv("SECRET_KEY", "aardvark")
    EMAIL_TOKEN_SALT = os.getenv("EMAIL_TOKEN_SALT", "aardvark")
    EMAIL_TOKEN_EXPIRY = int(os.getenv("EMAIL_TOKEN_EXPIRY", "259200"))
    PARTY_SCHEMA = os.getenv("PARTY_SCHEMA", "ras_party/schemas/party_schema.json")

    DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "partysvc")
    DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres")

    SECURITY_USER_NAME = os.getenv("SECURITY_USER_NAME", "admin")
    SECURITY_USER_PASSWORD = os.getenv("SECURITY_USER_PASSWORD", "secret")

    # dependencies
    AUTH_URL = os.getenv("AUTH_URL")
    CASE_URL = os.getenv("CASE_URL")
    COLLECTION_EXERCISE_URL = os.getenv("COLLECTION_EXERCISE_URL")
    FRONTSTAGE_URL = os.getenv("FRONTSTAGE_URL")
    IAC_URL = os.getenv("IAC_URL")
    SURVEY_URL = os.getenv("SURVEY_URL")

    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "test-project-id")
    PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "ras-rm-notify-test")

    NOTIFY_URL = os.getenv("NOTIFY_URL", "http://notify-gateway-service/emails/")
    NOTIFY_EMAIL_VERIFICATION_TEMPLATE = os.getenv("NOTIFY_EMAIL_VERIFICATION_TEMPLATE", "email_verification_id")
    NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE", "request_password_change_id"
    )
    NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE", "confirm_password_change_id"
    )
    NOTIFY_VERIFY_ACCOUNT_EMAIL_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_VERIFY_ACCOUNT_EMAIL_CHANGE_TEMPLATE", "verify_account_email_change"
    )
    NOTIFY_CONFIRM_ACCOUNT_EMAIL_CHANGE_TEMPLATE = os.getenv(
        "NOTIFY_CONFIRM_ACCOUNT_EMAIL_CHANGE_TEMPLATE", "confirm_account_email_change"
    )
    NOTIFY_ACCOUNT_LOCKED_TEMPLATE = os.getenv("NOTIFY_ACCOUNT_LOCKED_TEMPLATE", "account_locked_id")

    SHARE_SURVEY_ACCESS_NEW_ACCOUNT_TEMPLATE = os.getenv(
        "SHARE_SURVEY_ACCESS_NEW_ACCOUNT_TEMPLATE", "share_survey_access_new_account"
    )

    SHARE_SURVEY_ACCESS_EXISTING_ACCOUNT_TEMPLATE = os.getenv(
        "SHARE_SURVEY_ACCESS_EXISTING_ACCOUNT_TEMPLATE", "share_survey_access_existing_account"
    )

    SHARE_SURVEY_ACCESS_CANCELLATION_TEMPLATE = os.getenv(
        "SHARE_SURVEY_ACCESS_CANCELLATION_TEMPLATE", "share_survey_access_cancellation"
    )

    SHARE_SURVEY_ACCESS_CONFIRMATION_TEMPLATE = os.getenv(
        "SHARE_SURVEY_ACCESS_CONFIRMATION_TEMPLATE", "share_survey_access_confirmation"
    )

    TRANSFER_SURVEY_ACCESS_NEW_ACCOUNT_TEMPLATE = os.getenv(
        "TRANSFER_SURVEY_ACCESS_NEW_ACCOUNT_TEMPLATE", "transfer_survey_access_new_account"
    )

    TRANSFER_SURVEY_ACCESS_EXISTING_ACCOUNT_TEMPLATE = os.getenv(
        "TRANSFER_SURVEY_ACCESS_EXISTING_ACCOUNT_TEMPLATE", "transfer_survey_access_existing_account"
    )

    TRANSFER_SURVEY_ACCESS_CANCELLATION_TEMPLATE = os.getenv(
        "TRANSFER_SURVEY_ACCESS_CANCELLATION_TEMPLATE", "transfer_survey_access_cancellation"
    )

    TRANSFER_SURVEY_ACCESS_CONFIRMATION_TEMPLATE = os.getenv(
        "TRANSFER_SURVEY_ACCESS_CONFIRMATION_TEMPLATE", "transfer_survey_access_confirmation"
    )

    ACCOUNT_DELETION_CONFIRMATION_TEMPLATE = os.getenv(
        "ACCOUNT_DELETION_CONFIRMATION_TEMPLATE", "account_deletion_confirmation"
    )

    SEND_EMAIL_TO_GOV_NOTIFY = _is_true(os.getenv("SEND_EMAIL_TO_GOV_NOTIFY", True))


class DevelopmentConfig(Config):
    DEBUG = True
    LOGGING_LEVEL = "DEBUG"
    SURVEY_URL = os.getenv("SURVEY_URL", "http://localhost:8080")


class TestingConfig(DevelopmentConfig):
    DEBUG = True
    LOGGING_LEVEL = "ERROR"
    SECRET_KEY = "aardvark"
    PARTY_SCHEMA = "ras_party/schemas/party_schema.json"
    SECURITY_USER_NAME = "username"
    SECURITY_USER_PASSWORD = "password"
    DATABASE_SCHEMA = "partysvc"

    AUTH_URL = "http://mockhost:4444"
    CASE_URL = "http://mockhost:1111"
    COLLECTION_EXERCISE_URL = "http://mockhost:2222"
    FRONTSTAGE_URL = "http://dummy.ons.gov.uk"
    IAC_URL = "http://mockhost:6666"
    NOTIFY_URL = "http://mockhost:5555/emails/"

    GOOGLE_CLOUD_PROJECT = "test-project-id"
    PUBSUB_TOPIC = "ras-rm-notify-test"

    NOTIFY_EMAIL_VERIFICATION_TEMPLATE = "email_verification_id"
    NOTIFY_REQUEST_PASSWORD_CHANGE_TEMPLATE = "request_password_change_id"
    NOTIFY_CONFIRM_PASSWORD_CHANGE_TEMPLATE = "confirm_password_change_id"
    NOTIFY_ACCOUNT_LOCKED_TEMPLATE = "account_locked_id"

    SEND_EMAIL_TO_GOV_NOTIFY = True
