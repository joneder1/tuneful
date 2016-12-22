import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

#JSON Schema describing the structure of a song
song_schema = {
        "properties": {
            "file": {
                "filename": {"type" : "string"}
            }
        },
        "required": ["file"]
}

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """return a list of all songs in JSON"""
    #query all songs in the Song Database
    songs = session.query(models.Song).all()
    #returns songs in JSON
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def song_post():
    data = request.json
    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    #use the file ID to make sure that the file exists in the database, and make the relationship with your new song
    file = session.query(models.File).get(data['file']['id'])
    if not file:
        data = {"message": "File id {} not found".format(id)}
        return Response(json.dumps(data), 404, mimetype="application/json")
    
    #Add the song to the database 
    song = models.Song(file=file)
    session.add(song)
    session.commit()
    
    # Return a 201 Created, containing the song as JSON and with the
    # location header set to the location of the song
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get", id=song.id)}
    return Response(data, 201, headers=headers,
                mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)
    
@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")    
    


