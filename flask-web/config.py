import os
from dotenv import load_dotenv, find_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
uploaddir = os.path.join('instance','patients')

try:
    load_dotenv(find_dotenv(raise_error_if_not_found=True))
    secret = os.getenv('SECRET_KEY')
    db_url = os.getenv('DB_URL')
except OSError:
    secret = "anothersecret"
    db_url = None

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = secret
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = uploaddir
    SEND_FILE_MAX_AGE_DEFAULT = 24

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    ENV = 'development'
    DEBUG = True


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class TestingConfig(Config):
    TESTING = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
