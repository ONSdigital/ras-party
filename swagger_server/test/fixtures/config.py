test_config = """
service:
    name: ras-party
    version: 0.0.1
    scheme: http
    host: 0.0.0.0
    port: 8000
    log_level: error

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
