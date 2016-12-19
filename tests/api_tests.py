import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO
from io import BytesIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())
    
    def test_get_songs(self):
        """ Get all songs from database """
        #add test songs to DB
        file1 = models.File(filename="test1.mp3")
        file2 = models.File(filename="test2.mp3")
        song1 = models.Song(file=file1)
        song2 = models.Song(file=file2)
        
        session.add_all([song1, song2])
        session.commit()
        
        response = self.client.get("/api/songs",
            headers=[("Accept", "application/json")]
        )
        #should respond OK, two total added to DB
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)
        #song file and name should match with .MP3
        song1 = data[0]
        self.assertEqual(song1["file"]["name"], "test1.mp3")
        
        song2 = data[1]
        self.assertEqual
        
    def test_post_song(self):
        """ Adding a new song """
        
        file = models.File(filename="post_song.mp3")
        session.add(file)
        session.commit()

        data = {
            "file": {
                "id": file.id
            }
        }
        
        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        #why is this failing? AssertionError: '/api/songs' != '/api/songs/1'
        self.assertEqual(urlparse(response.headers.get("Location")).path,
            "/api/songs/1")
            
        data = json.loads(response.data.decode("ascii"))
        
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["name"], "post_song.mp3")
        
        songs = session.query(models.File).all()
        self.assertEqual(len(songs), 1)
        
        song = songs[0]
        self.assertEqual(song.filename, "post_song.mp3")
        
    def test_get_uploaded_file(self):
        path =  upload_path("test.txt")
        with open(path, "wb") as f:
            f.write(b"File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"File contents")
    
    def test_file_upload(self):
        data = {
            "file": (BytesIO(b"File contents"), "test.txt")
        }

        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")

        path = upload_path("test.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b"File contents")
        
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


