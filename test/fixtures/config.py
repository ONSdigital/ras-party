test_config = """
service:
    NAME: ras-party
    VERSION: 0.0.1
    SCHEME: http
    HOST: 0.0.0.0
    PORT: 8000
    LOG_LEVEL: error
    SECRET_KEY: aardvark
    EMAIL_TOKEN_SALT: bulbous
    PARTY_SCHEMA: ras_party/schemas/party_schema.json
    SECURITY_USER_NAME: username
    SECURITY_USER_PASSWORD: password
    REQUESTS_GET_TIMEOUT: 99
    REQUESTS_POST_TIMEOUT: 99

dependencies:
    ras-party-db:
        service: rds
        plan: shared-psql
        schema: ras-party
        uri: "sqlite:///:memory:"
    public-website:
        scheme: http
        host: dummy.ons.gov.uk
        port: 80
    case-service:
        scheme: http
        host: mockhost
        port: 1111
    collectionexercise-service:
        scheme: http
        host: mockhost
        port: 2222
    survey-service:
        scheme: http
        host: mockhost
        port: 3333
    notify-service:
        api_key: notify_api_key
        service_id: sdc_service_id
        email_verification_template: email_verification_id
        reset_password_template: reset_password_id
    oauth2-service:
        scheme: http
        host: mockhost
        port: 4444
        client_id: "ons@ons.gov"
        client_secret: "password"
    iac-service:
        scheme: http
        host: mockhost
        port: 6666

features:
    skip_oauth_registration: true
"""
