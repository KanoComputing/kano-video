import os
import json


class Playlist(object):

    def __init__(self, name, filename=None):
        super(Playlist, self).__init__()

        self.name = name
        self.filename = filename

        if filename is not None:
            self.load_from_file(filename)
        else:
            self.playlist = []

    def load_from_file(self, filepath):
        data = open(filepath).read()

        self.playlist = json.loads(data)

    def save_to_file(self, filepath):
        with open(filepath, 'w') as savefile:
            json.dump(self.playlist, savefile)

    def save(self):
        self.save_to_file(self.filename)

    def add(self, video):
        self.playlist.append(video)


class PlaylistCollection(object):

    def __init__(self, dir):
        super(PlaylistCollection, self).__init__()

        self.collection = {}

        for file in os.listdir(dir):
            path = dir + '/' + file
            self.add(Playlist(file, filename=path))

    def add(self, playlist):
        self.collection[playlist.name] = playlist


playlistCollection = PlaylistCollection('playlists')


def add_playlist_handler(_, playlist):
    playlistCollection.add(playlist)


def add_to_playlist_handler(_, playlist, video):
    playlistCollection[playlist].add(video)
