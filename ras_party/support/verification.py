import logging

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
import structlog

from ras_party.exceptions import RasError


logger = structlog.wrap_logger(logging.getLogger(__name__))


def generate_email_token(email):
    secret_key = current_app.config["SECRET_KEY"]
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"]

    # TODO: eventually implement a service startup check for all required config values
    if secret_key is None or email_token_salt is None:
        msg = "SECRET_KEY or EMAIL_TOKEN_SALT are not configured."
        logger.error(msg)
        raise RasError(msg)

    timed_serializer = URLSafeTimedSerializer(secret_key)
    return timed_serializer.dumps(email, salt=email_token_salt)


def decode_email_token(token, duration):
    logger.info('Checking email verification token', token=token)

    timed_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    email_token_salt = current_app.config["EMAIL_TOKEN_SALT"]

    return timed_serializer.loads(token, salt=email_token_salt, max_age=duration)
