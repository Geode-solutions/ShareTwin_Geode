''' Flask configuration '''
import os

class Config(object):
    FLASK_ENV = os.environ.get('FLASK_ENV', default=None)
    ID = os.environ.get('ID', default=None)
    PORT = '5000'
    CORS_HEADERS = 'Content-Type'
    DATA_FOLDER = '/data'
    UPLOAD_FOLDER = '/uploads'
    LOCK_FOLDER = './lock'

class ProdConfig(Config):
    DEBUG = False
    TESTING = False
    SSL = 'adhoc'
    ORIGINS = ['https://friendly-dolphin-d9fdd1.netlify.app']

class DevConfig(Config):
    DEBUG = True
    TESTING = True
    SSL = None
    ORIGINS = 'http://localhost:3000'
