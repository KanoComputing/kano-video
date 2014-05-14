#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk

from kano.network import is_internet

from .ui_elements import TopBar, MenuBar, Contents
from .views import HomeView, LocalView, YoutubeView, \
    PlaylistView, PlaylistCollectionView


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='Kano Video')

        self._win_width = 900
        self._contents_height = 550

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        top_bar = TopBar('Kano Video')
        self.grid.attach(top_bar, 0, 0, 1, 1)

        menu_bar = MenuBar(self.switch_to_home, self.switch_to_local,
                           self.switch_to_playlist_collection, self.switch_to_youtube)
        self.grid.attach(menu_bar, 0, 1, 1, 1)

        if is_internet():
            pass
        self.view = HomeView()

        self.contents = Contents(self.grid)
        self.contents.set_contents(self.view)
        self.contents.set_size_request(self._win_width, self._contents_height)

        self.grid.attach(self.contents, 0, 2, 1, 1)

    def switch_to_home(self, _button):
        self.view = HomeView()
        self.contents.set_contents(self.view)

    def switch_to_playlist_collection(self, _button):
        self.view = PlaylistCollectionView(self.switch_to_playlist)
        self.contents.set_contents(self.view)

    def switch_to_playlist(self, _button, playlist):
        self.view = PlaylistView(playlist)
        self.contents.set_contents(self.view)

    def switch_to_youtube(self, _button):
        self.view = YoutubeView()
        self.contents.set_contents(self.view)

    def switch_to_local(self, _button):
        self.view = LocalView()
        self.contents.set_contents(self.view)

    def dir_dialog(self):
        dialog = Gtk.FileChooserDialog(
            "Please select a folder", self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)

        # Set up file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Video files")
        filter_text.add_pattern('*.mkv')
        dialog.add_filter(filter_text)

        dialog.set_current_folder(os.path.expanduser('~'))

        response = dialog.run()

        dir_path = None
        if response == Gtk.ResponseType.OK:
            dir_path = dialog.get_filename()
        dialog.destroy()
        return dir_path
