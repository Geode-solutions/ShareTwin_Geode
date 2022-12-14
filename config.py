''' Flask configuration '''
import os

class Config(object):
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', default=None)
    PORT = '5000'
    CORS_HEADERS = 'Content-Type'
    UPLOAD_FOLDER = '/data'
    LOCK_FOLDER = './lock'

class ProdConfig(Config):
    ORIGINS = ['https://share-twin.com', 'https://next.share-twin.com']

class DevConfig(Config):
    ORIGINS = 'http://localhost:3000'
