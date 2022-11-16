''' Packages '''
import os
import dotenv
import threading

import flask
import flask_cors

import blueprint_geode

if os.path.isfile('./.env'):
    basedir = os.path.abspath(os.path.dirname(__file__))
    dotenv.load_dotenv(os.path.join(basedir, '.env'))

''' Global config '''
app = flask.Flask(__name__)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.daemon = True
    t.start()
    return t

def kill():
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if len(os.listdir(LOCK_FOLDER)) == 0:
        os._exit(0)
    if os.path.isfile(LOCK_FOLDER + '/ping.txt'):
        os.remove(LOCK_FOLDER + '/ping.txt')

''' Config variables '''
FLASK_ENV = os.environ.get('FLASK_ENV', default=None)

if FLASK_ENV == "production" or FLASK_ENV == "test":
    app.config.from_object('config.ProdConfig')
    # set_interval(kill, 45)
else:
    app.config.from_object('config.DevConfig')

ID = app.config.get('ID')
PORT = int(app.config.get('PORT'))
CORS_HEADERS = app.config.get('CORS_HEADERS')
UPLOAD_FOLDER = app.config.get('UPLOAD_FOLDER')
LOCK_FOLDER = app.config.get('LOCK_FOLDER')
DEBUG = app.config.get('DEBUG')
TESTING = app.config.get('TESTING')
ORIGINS = app.config.get('ORIGINS')
SSL = app.config.get('SSL')

app.register_blueprint(blueprint_geode.geode_routes)

flask_cors.CORS(app, origins=ORIGINS)

# ''' Main '''
if __name__ == '__main__':
    print('Python is running in ' + FLASK_ENV + ' mode')
    print(f'{ID=}')
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT, ssl_context=SSL)
