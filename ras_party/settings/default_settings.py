class Config:
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'banana'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
