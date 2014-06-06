import os
import json

playlist_dir = 'playlists'


class Playlist(object):

    def __init__(self, name):
        super(Playlist, self).__init__()

        self.name = name
        self.filename = playlist_dir + '/' + name + '.json'

        self.load()

    def load_from_file(self, filepath):
        with open(filepath) as openfile:
            raw_data = openfile.read()

            data = json.loads(raw_data)

            if len(data) is not 0 and 'permanent' in data[0]:
                self.permanent = data[0]['permanent']
                del data[0]
            else:
                self.permanent = False

            self.playlist = data

    def load(self):
        try:
            self.load_from_file(self.filename)
        except IOError:
            self.playlist = []
            self.permanent = False
            self.save()

    def save_to_file(self, filepath):
        with open(filepath, 'w') as savefile:
            data = self.playlist[:]
            data.insert(0, {'permanent': self.permanent})
            json.dump(data, savefile)

    def save(self):
        self.save_to_file(self.filename)

    def add(self, video):
        self.playlist.append(video)

    def delete(self):
        try:
            os.remove(self.filename)
        except IOError:
            pass

    def remove(self, video):
        self.playlist.remove(video)


class PlaylistCollection(object):

    def __init__(self, dir):
        super(PlaylistCollection, self).__init__()

        self.collection = {}

        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)

        for file in os.listdir(dir):
            filename = os.path.splitext(file)[0]
            self.add(Playlist(filename))

    def add(self, playlist):
        self.collection[playlist.name] = playlist

    def delete(self, playlist_name):
        self.collection[playlist_name].delete()
        del self.collection[playlist_name]

    def save(self):
        for _, playlist in self.collection.iteritems():
            playlist.save()


playlistCollection = PlaylistCollection('playlists')
