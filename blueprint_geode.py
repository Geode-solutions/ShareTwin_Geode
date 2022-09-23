import flask
import flask_cors
import os
import functions
import werkzeug
import GeodeObjects

geode_routes = flask.Blueprint('geode_routes', __name__)
flask_cors.CORS(geode_routes)

@geode_routes.before_request
def before_request():
    functions.create_lock_file()

@geode_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()

@geode_routes.route('/uploadfile', methods=['POST'])
def vaditychecker_uploadfile():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object = flask.request.form.get('object')
        file = flask.request.form.get('file')
        filename = flask.request.form.get('filename')
        filesize = flask.request.form.get('filesize')
        extension = flask.request.form.get('extension')

        secureFilename = werkzeug.utils.secure_filename(filename)
        filePath = os.path.join(UPLOAD_FOLDER, secureFilename)
        strictFileName = os.path.splitext(secureFilename)[0]
        newFileName = strictFileName + '.' + extension

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
        
        uploadedFile = functions.UploadFile(file, filename, UPLOAD_FOLDER, filesize)
        if not uploadedFile:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        newFilePath = os.path.join(UPLOAD_FOLDER, newFileName)
        model = GeodeObjects.ObjectsList()[object]['load'](filePath)
        functions.GeodeObjects.ObjectsList()[object]['save'](model, newFilePath)
            
        return flask.make_response({"newFilename": newFileName}, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

