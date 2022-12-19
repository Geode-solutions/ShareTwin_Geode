import flask
import flask_cors
import os
import functions
import werkzeug
import geode_objects
import uuid

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
def createbackend():
    return flask.make_response({"ID": str("123456")}, 200)
@geode_routes.route('/healthcheck', methods=['GET'])
def healthcheck():
    return flask.make_response({"message": "healthy"}, 200)
@geode_routes.route('/ping', methods=['GET', 'POST'])
def ping():
    LOCK_FOLDER = flask.current_app.config['LOCK_FOLDER']
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + '/ping.txt'):
        f = open(LOCK_FOLDER + '/ping.txt', 'a')
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)

@geode_routes.route('/uploadfile', methods=['POST'])
def uploadfile():
    try:
        DATA_FOLDER = flask.current_app.config['DATA_FOLDER']
        file = flask.request.form.get('file')
        filename = flask.request.form.get('filename')
        filesize = flask.request.form.get('filesize')
        
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if filename is None:
            return flask.make_response({"error_message": "No filename sent"}, 400)
        if filesize is None:
            return flask.make_response({"error_message": "No filesize sent"}, 400)
        
        newFileName = werkzeug.utils.secure_filename(filename)
        uploadedFile = functions.UploadFile(file, newFileName, DATA_FOLDER, filesize)
        if not uploadedFile:
            flask.make_response({"error_message": "File not uploaded"}, 500)
            
        return flask.make_response({"newFilename": newFileName}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

@geode_routes.route('/convertfile', methods=['POST'])
def convertfile():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object = flask.request.form.get('object')
        file = flask.request.form.get('file')
        filename = flask.request.form.get('filename')
        filesize = flask.request.form.get('filesize')
        extension = flask.request.form.get('extension')

        if object is None:
            return flask.make_response({"error_message": "No object sent"}, 400)
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if filename is None:
            return flask.make_response({"error_message": "No filename sent"}, 400)
        if filesize is None:
            return flask.make_response({"error_message": "No filesize sent"}, 400)
        if extension is None:
            return flask.make_response({"error_message": "No extension sent"}, 400)
        
        secureFilename = werkzeug.utils.secure_filename(filename)
        filePath = os.path.join(UPLOAD_FOLDER, secureFilename)
        strictFileName = os.path.splitext(secureFilename)[0]
        newFileName = strictFileName + '.' + extension

        uploadedFile = functions.UploadFile(file, filename, UPLOAD_FOLDER, filesize)
        if not uploadedFile:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        newFilePath = os.path.join(UPLOAD_FOLDER, newFileName)
        model = geode_objects.objects_list()()[object]['load'](filePath)
        functions.geode_objects.objects_list()[object]['save'](model, newFilePath)
            
        return flask.make_response({"newFilename": newFileName}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)