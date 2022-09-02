import flask
import flask_cors
import os
import functions
import werkzeug
import GeodeObjects

validitychecker_routes = flask.Blueprint('validitychecker_routes', __name__)
flask_cors.CORS(validitychecker_routes)

@validitychecker_routes.before_request
def before_request():
    functions.create_lock_file()

@validitychecker_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()

@validitychecker_routes.route('/versions', methods=['GET'])
def validitychecker_versions():
    list_packages = ['OpenGeode-core', 'OpenGeode-IO', 'OpenGeode-Geosciences', 'OpenGeode-GeosciencesIO', 'OpenGeode-Inspector']
    return flask.make_response({"versions": functions.GetVersions(list_packages)}, 200)

@validitychecker_routes.route('/allowedfiles', methods=['GET'])
def vaditychecker_allowedfiles():
    extensions = functions.ListAllInputExtensions()
    return {"status": 200, "extensions": extensions}

@validitychecker_routes.route('/allowedobjects', methods=['POST'])
def validitychecker_allowedobjects():
    filename = flask.request.form.get('filename')
    if filename is None:
        return flask.make_response({"error_message": "No file sent"}, 400)
    file_extension = os.path.splitext(filename)[1][1:]
    objects = functions.ListObjects(file_extension)
    return flask.make_response({"objects": objects}, 200)

@validitychecker_routes.route('/uploadfile', methods=['POST'])
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

