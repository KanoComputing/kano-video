# popup.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The collection of popup widgets that might be used
#


import os
from gi.repository import Gtk

from kano.gtk3.kano_dialog import KanoDialog
from kano.gtk3.kano_combobox import KanoComboBox
from kano_video.logic.playlist import Playlist, playlistCollection

from .general import TopBar, Button


class PlaylistPopup(Gtk.Dialog):
    """
    A basis from which playlist-related popups can draw from
    """

    def __init__(self, main=None):
        super(PlaylistPopup, self).__init__(title='Kano Video')

        self._main_win = main

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
        if self._main_win:
            self._main_win.blur()

        self.show_all()
        super(PlaylistPopup, self).run()

        if self._main_win:
            self._main_win.unblur()

        return self._return


class AddToPlaylistPopup(PlaylistPopup):
    """
    A popup for selecting a playlist
    """

    def __init__(self, video, main=None):
        super(AddToPlaylistPopup, self).__init__(main)

        self.video = video

        self._combo = KanoComboBox(max_display_items=7)
        self._combo.connect('changed', self._enable_add)
        self.grid.attach(self._combo, 0, 1, 1, 1)

        self._add_button = Button('ADD')
        self._add_button.get_style_context().add_class('green')
        self._add_button.set_sensitive(False)
        self._add_button.connect('clicked', self._add, self._combo)
        self.grid.attach(self._add_button, 1, 1, 1, 1)

        button = Button('CREATE NEW')
        button.get_style_context().add_class('orange_linktext')
        button.connect('clicked', self._new)
        self.grid.attach(button, 0, 2, 1, 1)

        self.refresh()

    def _enable_add(self, _):
        self._add_button.set_sensitive(True)

    def _add(self, _, combo):
        playlist_name = combo.get_selected_item_text()
        playlistCollection.collection[playlist_name].add(self.video)

        self._return = playlist_name
        self.destroy()

    def _new(self, _):
        popup = AddPlaylistPopup(self._main_win)
        res = popup.run()
        if res:
            self._combo.append(res)
            self._combo.set_selected_item_index(0)

            self._combo.set_sensitive(True)

    def refresh(self):
        self._combo.remove_all()
        for name, _ in playlistCollection.collection.iteritems():
            if name != 'Kano':
                self._combo.append(name)

        if len(playlistCollection.collection) is 1:
            self._combo.set_sensitive(False)


class AddPlaylistPopup(PlaylistPopup):
    """
    A popup for playlist creation
    """

    def __init__(self, main=None):
        super(AddPlaylistPopup, self).__init__(main)

        entry = Gtk.Entry()
        entry.connect('activate', self._add, entry)
        entry.connect('key-release-event', self._validate_entry, entry)
        self.grid.attach(entry, 0, 1, 1, 1)

        self._add_button = Button('ADD')
        self._add_button.get_style_context().add_class('green')
        self._add_button.set_sensitive(False)
        self._add_button.connect('clicked', self._add, entry)
        self.grid.attach(self._add_button, 1, 1, 1, 1)

    def _add(self, _, playlist_entry):
        playlist_name = playlist_entry.get_text()

        if playlist_name == 'Kano':
            confirm = KanoDialog('You can\'t add to the "Kano" playlist',
                                 '',
                                 {'BACK': {'return_value': True,
                                           'color': 'red'}},
                                 parent_window=self._main_win)
            confirm.run()
            return

        if playlist_name in playlistCollection.collection:
            confirm = KanoDialog(
                'The playlist "{}" already exists!'.format(playlist_name),
                'Do you want to add the video to this playlist or try again?',
                {'USE PLAYLIST': {'return_value': True},
                 'TRY AGAIN': {'return_value': False, 'color': 'red'}},
                parent_window=self._main_win)
            response = confirm.run()
            if not response:
                return
        else:
            playlist = Playlist(playlist_name)
            playlistCollection.add(playlist)

        self._return = playlist_name
        self.destroy()

    def _validate_entry(self, _, __, playlist_entry):
        playlist_name = playlist_entry.get_text()

        if playlist_name == '':
            enabled = False
        else:
            enabled = True

        self._add_button.set_sensitive(enabled)


class LoadFilePopup(Gtk.FileChooserDialog):
    """
    A file selection dialog
    """

    def __init__(self, main=None):
        super(LoadFilePopup, self).__init__(
            "Please select a folder", self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self._main_win = main

        # Set up file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Video files")

        file_extensions = ['mkv',
                           'm4v',
                           'mp4',
                           'avi',
                           'flv',
                           'mov',
                           'ogg',
                           'wmv'
                          ]

        for ext in file_extensions:
            filter_text.add_pattern('*.{}'.format(ext))

        self.add_filter(filter_text)

        self.set_current_folder(os.path.expanduser('~'))

    def run(self):
        self._main_win.blur()
        response = super(LoadFilePopup, self).run()
        self._main_win.unblur()

        dir_path = None
        if response == Gtk.ResponseType.OK:
            dir_path = self.get_filename()
        self.destroy()
        return dir_path
