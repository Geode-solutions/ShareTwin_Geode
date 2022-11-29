import flask
import flask_cors
import os
import functions
import werkzeug
import geode_objects
import uuid4

geode_routes = flask.Blueprint('geode_routes', __name__)
flask_cors.CORS(geode_routes)

@geode_routes.before_request
def before_request():
    functions.create_lock_file()

@geode_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()

@geode_routes.route('/', methods=['GET'])
def root():
    return flask.make_response({"message": "root"}, 200)
@geode_routes.route('/sharetwin/createbackend', methods=['POST', 'OPTIONS'])
def create_backend():
    return flask.make_response({"ID": str("123456")}, 200)
@geode_routes.route('/healthcheck', methods=['GET'])
def healthcheck():
    return flask.make_response({"message": "healthy"}, 200)
@geode_routes.route('/ping', methods=['POST'])
def ping():
    LOCK_FOLDER = flask.current_app.config['LOCK_FOLDER']
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + '/ping.txt'):
        f = open(LOCK_FOLDER + '/ping.txt', 'a')
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)

@geode_routes.route('/uploadfile', methods=['POST'])
def upload_file():
    try:
        ID = str(uuid.uuid4()).replace('-', '')
        DATA_FOLDER = flask.current_app.config['DATA_FOLDER']
        file = flask.request.form.get('file')
        file_name = flask.request.form.get('file_name')
        file_size = flask.request.form.get('file_size')
        
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if file_name is None:
            return flask.make_response({"error_message": "No file_name sent"}, 400)
        if file_size is None:
            return flask.make_response({"error_message": "No filesize sent"}, 400)
        
        file_extension = os.path.splitext(file_name)[1]
        new_file_name = ID + file_extension
        uploaded_file = functions.upload_file(file, new_file_name, DATA_FOLDER, file_size)
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)
            
        return flask.make_response({"newFilename": new_file_name, 'displayed_file_name': file_name}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

@geode_routes.route('/convertfile', methods=['POST'])
def convert_file():
    try:
        ID = str(uuid.uuid4()).replace('-', '')
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object = flask.request.form.get('object')
        file = flask.request.form.get('file')
        file_name = flask.request.form.get('file_name')
        file_size = flask.request.form.get('file_size')
        extension = flask.request.form.get('extension')

        if object is None:
            return flask.make_response({"error_message": "No object sent"}, 400)
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if file_name is None:
            return flask.make_response({"error_message": "No file_name sent"}, 400)
        if file_size is None:
            return flask.make_response({"error_message": "No file_size sent"}, 400)
        if extension is None:
            return flask.make_response({"error_message": "No extension sent"}, 400)
        
        secure_file_name = werkzeug.utils.secure_filename(file_name)
        file_path = os.path.join(UPLOAD_FOLDER, secure_file_name)
        strict_file_name = os.path.splitext(secure_file_name)[0]
        new_file_name = ID + '.' + extension

        uploaded_file = functions.upload_file(file, file_name, UPLOAD_FOLDER, filesize)
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        newFilePath = os.path.join(UPLOAD_FOLDER, new_file_name)
        model = geode_objects.ObjectsList()[object]['load'](file_path)
        functions.geode_objects.ObjectsList()[object]['save'](model, newFilePath)
            
        return flask.make_response({"newFilename": new_file_name}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)