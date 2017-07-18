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

features:
    skip_oauth_registration: true
"""
