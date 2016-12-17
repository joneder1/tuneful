import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

#integer id column, and a column specifying a one-to-one relationship with a File.
class Song(Base):
    __tablename__ = "songs"
    
    #one to one relationship with a File
    id = Column(Integer, primary_key=True)
    #establish relationship with File
    file = relationship("File", uselist=False, backref="song")
    #return results as dictionary showing id and file
    def as_dictionary(self):
        return {
            "id": self.id,
            #return file as dictionary
            "file": self.file.as_dictionary()
        }    
#integer id column, a string column for the filename, and the backref from the one-to-one relationship with the Song.
class File(Base):
    __tablename__ = "files"
    
    #one to one relationship with Song
    id = Column(Integer, primary_key=True)
    filename = Column(String(1024))
    song_id = Column(Integer, ForeignKey('songs.id'))
    
    #{"id": 7, "name": "Shady_Grove.mp3"}
    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.filename
        }            
