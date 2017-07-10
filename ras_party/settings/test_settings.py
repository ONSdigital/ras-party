class Config:
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'banana'

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # TODO: eventually eliminate ENVIRONMENT_NAME
    ENVIRONMENT_NAME = 'test'
    # TODO: unify the yaml config with Flask config, e.g. configure Flask from yaml
    CONFIG_PATH = './fixtures/config.yaml'
