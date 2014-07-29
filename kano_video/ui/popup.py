# popup.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#


import os
from gi.repository import Gtk

from kano_video.logic.playlist import Playlist, playlistCollection

from .general import TopBar, Button


class PlaylistPopup(Gtk.Dialog):

    def __init__(self):
        super(PlaylistPopup, self).__init__(title='Kano Video')

        self.get_style_context().add_class('popup')
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        popup_grid = Gtk.Grid()

        self._bar = TopBar('')
        popup_grid.attach(self._bar, 0, 0, 1, 1)

        content = Gtk.Alignment(xalign=0.5, yalign=0.5)
        content.set_padding(30, 20, 50, 50)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(20)
        content.add(self.grid)

        popup_grid.attach(content, 0, 1, 1, 1)

        self.get_content_area().add(popup_grid)

        self._return = None

    def run(self):
        self.show_all()
        super(PlaylistPopup, self).run()

        return self._return


class AddToPlaylistPopup(PlaylistPopup):

    def __init__(self, video):
        super(AddToPlaylistPopup, self).__init__()

        self.video = video

        self._combo = Gtk.ComboBoxText.new()
        self.grid.attach(self._combo, 0, 1, 1, 1)

        self._add_button = Button('ADD')
        self._add_button.get_style_context().add_class('green')
        self._add_button.connect('clicked', self._add, self._combo)
        self.grid.attach(self._add_button, 1, 1, 1, 1)

        button = Button('CREATE NEW')
        button.get_style_context().add_class('orange_linktext')
        button.connect('clicked', self._new)
        self.grid.attach(button, 0, 2, 1, 1)

        self.refresh()

    def _add(self, _, playlist_entry):
        playlist_name = playlist_entry.get_active_text()
        playlistCollection.collection[playlist_name].add(self.video)

        self._return = playlist_name
        self.destroy()

    def _new(self, _):
        popup = AddPlaylistPopup()
        res = popup.run()
        if res:
            self._combo.prepend_text(res)
            self._combo.set_active(0)

            self._add_button.set_sensitive(True)
            self._combo.set_button_sensitivity(Gtk.SensitivityType.ON)

    def refresh(self):
        model = self._combo.get_model()
        model.clear()
        for name, _ in playlistCollection.collection.iteritems():
            if name != 'Kano':
                self._combo.append_text(name)

        if len(playlistCollection.collection) is 1:
            self._add_button.set_sensitive(False)
            self._combo.set_button_sensitivity(Gtk.SensitivityType.OFF)


class AddPlaylistPopup(PlaylistPopup):

    def __init__(self):
        super(AddPlaylistPopup, self).__init__()

        entry = Gtk.Entry()
        entry.connect('activate', self._add, entry)
        self.grid.attach(entry, 0, 1, 1, 1)

        button = Button('ADD')
        button.get_style_context().add_class('green')
        button.connect('clicked', self._add, entry)
        self.grid.attach(button, 1, 1, 1, 1)

    def _add(self, _, playlist_entry):
        playlist_name = playlist_entry.get_text()

        playlist = Playlist(playlist_name)
        playlistCollection.add(playlist)

        self._return = playlist_name
        self.destroy()


class LoadFilePopup(Gtk.FileChooserDialog):

    def __init__(self):
        super(LoadFilePopup, self).__init__(
            "Please select a folder", self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # Set up file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Video files")
        filter_text.add_pattern('*.mkv')
        self.add_filter(filter_text)

        self.set_current_folder(os.path.expanduser('~'))

    def run(self):
        response = super(LoadFilePopup, self).run()

        dir_path = None
        if response == Gtk.ResponseType.OK:
            dir_path = self.get_filename()
        self.destroy()
        return dir_path
