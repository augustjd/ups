import os


class Config:
    """Base configuration."""

    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    DEFAULT_LOCALE = 'en'

    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

    #
    # SQLAlchemy
    #
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../dev.db'
    SQLALCHEMY_BINDS = {
        'users': 'users.dev.db',
        'packages': 'packages.dev.db',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestConfig(DevConfig):
    ENV = 'test'
    TESTING = True
    DEBUG = True

    #
    # SQLAlchemy
    #
    SQLALCHEMY_BINDS = {
        'users': 'sqlite://',
        'packages': 'sqlite://',
    }
    SQLALCHEMY_ECHO = False  # Prints all SQL to stdout

    #
    # AWS
    #
    AWS_ACCESS_KEY_ID = 'INVALID'
    AWS_SECRET_ACCESS_KEY = 'INVALID'

    #
    # STORAGE
    #
    STORAGE_DEFAULT_SERVICE = 's3'
    STORAGE_DEFAULT_BUCKET = 'BUCKET'
    STORAGE_DEFAULT_LOCATION = 'LOCATION'
