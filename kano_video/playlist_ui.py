from gi.repository import Gtk

from .general_ui import KanoWidget


class PlaylistList(KanoWidget):

    def __init__(self, playlists, playlist_cb):
        super(PlaylistList, self).__init__()

        i = 0
        for name, p in playlists.iteritems():
            button = Gtk.Button(name)
            button.connect('clicked', playlist_cb, name)
            self._grid.attach(button, 0, i, 1, 1)
            i += 1
