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
    """Add a new song to the database"""
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

file1 = models.File(filename="test1.mp3")
file2 = models.File(filename="test2.mp3")
song1 = models.Song(file=file1)
song2 = models.Song(file=file2)
        


