test_config = """
service:
    NAME: ras-party
    VERSION: 0.0.1
    SCHEME: http
    HOST: 0.0.0.0
    PORT: 8000
    LOG_LEVEL: error

dependencies:
    ras-party-db:
        service: rds
        plan: shared-psql
        schema: ras-party
        uri: "sqlite:///:memory:"
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
    gov-uk-notify-service:
        gov_notify_api_key: notify_api_key_placeholder
        gov_notify_template_id: notify_template_id_placeholder
        gov_notify_service_id: notify_service_id__placeholder

features:
    skip_oauth_registration: true
"""
