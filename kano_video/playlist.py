import os
import json


class Playlist(object):

    def __init__(self, name):
        super(Playlist, self).__init__()

        self._dir = 'playlists'
        self.name = name
        self.filename = self._dir + '/' + name + '.json'

        self.load()

    def load_from_file(self, filepath):
        with open(filepath) as openfile:
            data = openfile.read()
            self.playlist = json.loads(data)

    def load(self):
        try:
            self.load_from_file(self.filename)
        except IOError:
            self.playlist = []

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
            filename = os.path.splitext(file)[0]
            self.add(Playlist(filename))

    def add(self, playlist):
        self.collection[playlist.name] = playlist

    def save(self):
        for _, playlist in self.collection.iteritems():
            playlist.save()


playlistCollection = PlaylistCollection('playlists')
