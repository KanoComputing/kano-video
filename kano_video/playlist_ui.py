from gi.repository import Gtk

from .playlist import playlistCollection

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


class PlaylistAddBar(KanoWidget):

    def __init__(self):
        super(PlaylistAddBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('playlist_add_bar')

        title_str = ''
        title = Gtk.Label(title_str)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(430, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        button = Gtk.Button('CREATE LIST')
        button.set_size_request(20, 20)
        button.connect('clicked', self._add_handler)
        self._grid.attach(button, 1, 0, 1, 1)

    def _add_handler(self, button):
        popup = AddPlaylistPopup()
        popup.show_all()


class PlaylistPopup(Gtk.Window):

    def __init__(self):
        super(PlaylistPopup, self).__init__(title='Kano Video')

        self._win_width = 300
        self._contents_height = 200

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()
        self.add(self.grid)

    def _add(self, button, playlist):
        print playlist


class AddToPlaylistPopup(PlaylistPopup):

    def __init__(self):
        super(AddToPlaylistPopup, self).__init__()

        combo = Gtk.ComboBoxText.new()
        for name, _ in playlistCollection.collection.iteritems():
            combo.append_text(name)

        self.grid.attach(combo, 0, 0, 1, 1)

        button = Gtk.Button('ADD')
        button.connect('clicked', self._add, combo.get_active_text())
        self.grid.attach(button, 1, 0, 1, 1)

        button = Gtk.Button('CREATE NEW')
        self.grid.attach(button, 0, 1, 1, 1)


class AddPlaylistPopup(PlaylistPopup):

    def __init__(self):
        super(AddPlaylistPopup, self).__init__()

        entry = Gtk.Entry()
        self.grid.attach(entry, 0, 0, 1, 1)

        button = Gtk.Button('ADD')
        button.connect('clicked', self._add, entry.get_text())
        self.grid.attach(button, 1, 0, 1, 1)
