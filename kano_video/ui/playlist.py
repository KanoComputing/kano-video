from gi.repository import Gtk

from kano_video.logic.playlist import playlistCollection

from .general import KanoWidget, RemoveButton

from kano.gtk3.kano_dialog import KanoDialog


class PlaylistEntry(Gtk.Button):

    def __init__(self, name):
        super(PlaylistEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        self.connect('clicked', self._playlist_handler, name)

        content = Gtk.Alignment()
        content.set_padding(20, 20, 20, 20)
        self.add(content)

        button_grid = Gtk.Grid()
        content.add(button_grid)

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

        remove = RemoveButton()
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
            win = self.get_toplevel()
            win.switch_view('playlist-collection')


class PlaylistList(KanoWidget):

    def __init__(self, playlists):
        super(PlaylistList, self).__init__()

        i = 0
        for name, p in playlists.iteritems():
            playlist = PlaylistEntry(name)
            self._grid.attach(playlist, 0, i, 1, 1)
            i += 1
