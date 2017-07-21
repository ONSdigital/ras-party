test_config = """
service:
    NAME: ras-party
    VERSION: 0.0.1
    SCHEME: http
    HOST: 0.0.0.0
    PORT: 8000
    LOG_LEVEL: error
    SECRET_KEY: aardvark

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
    frontstage-service:
        # TODO: find out the correct values
        scheme: http
        host: unknown
        port: unknown
    survey-service:
        scheme: http
        host: mockhost
        port: 3333
    gov-uk-notify-service:
        gov_notify_api_key: notify_api_key_placeholder
        gov_notify_template_id: notify_template_id_placeholder
        gov_notify_service_id: notify_service_id__placeholder
    oauth2-service:
        scheme: http
        host: mockhost
        port: 4444
        authorization_endpoint: "/web/authorize/"
        token_endpoint: "/api/v1/tokens/"
        admin_endpoint: "/api/account/create"
        client_id: "ons@ons.gov"
        client_secret: "password"
        
features:
    skip_oauth_registration: true
"""
