from gi.repository import Gtk

from .playlist import playlistCollection, Playlist

from .general_ui import KanoWidget
from .bar_ui import TopBar

from kano.gtk3.kano_dialog import KanoDialog


class PlaylistEntry(Gtk.Button):

    def __init__(self, name):
        super(PlaylistEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        self.connect('clicked', self._playlist_handler, name)

        button_grid = Gtk.Grid()
        self.add(button_grid)

        title = Gtk.Label(name, hexpand=True)
        title.set_alignment(0, 0.5)
        title.get_style_context().add_class('title')
        button_grid.attach(title, 0, 0, 1, 1)

        count = len(playlistCollection.collection[name].playlist)
        item = 'video'
        if count is not 1:
            item = '{}s'.format(item)

        subtitle_str = '{} {}'.format(count, item)
        subtitle = Gtk.Label(subtitle_str)
        subtitle.set_alignment(0, 0.5)
        subtitle.get_style_context().add_class('subtitle')
        button_grid.attach(subtitle, 0, 1, 1, 1)

        remove = Gtk.Button('REMOVE')
        remove.get_style_context().add_class('grey_linktext')
        remove.set_alignment(1, 0)
        remove.connect('clicked', self._remove_handler, name)
        button_grid.attach(remove, 1, 0, 1, 1)

    def _playlist_handler(self, _button, name):
        win = self.get_toplevel()
        win.switch_view('playlist', playlist=name)

    def _remove_handler(self, _button, _name):
        confirm = KanoDialog('Are you sure?',
                             'You are about to delete the playlist called "{}"'.format(_name),
                             {'OK': True, 'CANCEL': False})
        response = confirm.run()
        if response:
            playlistCollection.delete(_name)


class PlaylistList(KanoWidget):

    def __init__(self, playlists):
        super(PlaylistList, self).__init__()

        i = 0
        for name, p in playlists.iteritems():
            playlist = PlaylistEntry(name)
            self._grid.attach(playlist, 0, i, 1, 1)
            i += 1


class PlaylistAddBar(KanoWidget):

    def __init__(self):
        super(PlaylistAddBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('playlist_add_bar')

        title_str = ''
        title = Gtk.Label(title_str, hexpand=True)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(430, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        button = Gtk.Button('CREATE LIST')
        button.get_style_context().add_class('green')
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

        self._bar = TopBar('')
        self.grid.attach(self._bar, 0, 0, 2, 1)

        self.add(self.grid)


class AddToPlaylistPopup(PlaylistPopup):

    def __init__(self, video):
        super(AddToPlaylistPopup, self).__init__()

        self.video = video

        self._combo = Gtk.ComboBoxText.new()
        self.refresh()
        self.grid.attach(self._combo, 0, 1, 1, 1)

        button = Gtk.Button('ADD')
        button.get_style_context().add_class('green')
        button.connect('clicked', self._add, self._combo)
        self.grid.attach(button, 1, 1, 1, 1)

        button = Gtk.Button('CREATE NEW')
        button.get_style_context().add_class('green')
        button.connect('clicked', self._new)
        self.grid.attach(button, 0, 2, 1, 1)

    def _add(self, _, playlist_entry):
        playlist_name = playlist_entry.get_active_text()
        playlistCollection.collection[playlist_name].add(self.video)
        self.hide()

    def _new(self, _):
        popup = AddPlaylistPopup(caller=self)
        popup.show_all()

    def refresh(self):
        model = self._combo.get_model()
        model.clear()
        for name, _ in playlistCollection.collection.iteritems():
            self._combo.append_text(name)


class AddPlaylistPopup(PlaylistPopup):

    def __init__(self, caller=None):
        super(AddPlaylistPopup, self).__init__()

        self._caller = caller

        entry = Gtk.Entry()
        self.grid.attach(entry, 0, 1, 1, 1)

        button = Gtk.Button('ADD')
        button.get_style_context().add_class('green')
        button.connect('clicked', self._add, entry)
        self.grid.attach(button, 1, 1, 1, 1)

    def _add(self, _, playlist_entry):
        playlist = Playlist(playlist_entry.get_text())
        playlistCollection.add(playlist)
        self.hide()

        if self._caller is not None:
            self._caller.refresh()
