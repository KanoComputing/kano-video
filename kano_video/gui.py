#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk

from kano.network import is_internet
from .playlist import playlistCollection

from .general_ui import Contents
from .bar_ui import MenuBar
from .views import HomeView, LocalView, YoutubeView, \
    PlaylistView, PlaylistCollectionView, DetailView


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='Kano Video')

        self._win_width = 950
        self._contents_height = 550

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        menu_bar = MenuBar()
        self.grid.attach(menu_bar, 0, 0, 1, 1)

        if is_internet():
            pass
        self.view = HomeView()

        self.contents = Contents(self.grid)
        self.contents.set_contents(self.view)
        self.contents.set_size_request(self._win_width, self._contents_height)

        self.grid.attach(self.contents, 0, 1, 1, 1)

        self.connect('delete-event', self.on_close)

    def switch_view(self, view, playlist=None, search_keyword=None, users=False, video=None):
        views = {'home': self.switch_to_home,
                 'playlist-collection': self.switch_to_playlist_collection,
                 'playlist': self.switch_to_playlist,
                 'youtube': self.switch_to_youtube,
                 'library': self.switch_to_local,
                 'detail': self.switch_to_detail,
                 'previous': self.switch_to_previous}

        if view is 'playlist':
            views[view](playlist)
        elif view is 'youtube':
            views[view](search_keyword=search_keyword, users=users)
        elif view is 'detail':
            views[view](video=video)
        else:
            views[view]()

    def switch_to_home(self):
        self.view = HomeView()
        self.contents.set_contents(self.view)

    def switch_to_playlist_collection(self):
        self.view = PlaylistCollectionView()
        self.contents.set_contents(self.view)

    def switch_to_playlist(self, playlist):
        self.view = PlaylistView(playlist)
        self.contents.set_contents(self.view)

    def switch_to_youtube(self, search_keyword=None, users=False):
        self.view = YoutubeView()
        self.view.search_handler(search_keyword, users)
        self.contents.set_contents(self.view)

    def switch_to_local(self):
        self.view = LocalView()
        self.contents.set_contents(self.view)

    def switch_to_detail(self, video):
        self.prev_view = self.view
        self.view = DetailView(video)
        self.contents.set_contents(self.view)

    def switch_to_previous(self):
        if self.prev_view:
            self.view = self.prev_view
            self.contents.set_contents(self.view)

    def on_close(self, widget=None, event=None):
        playlistCollection.save()
        Gtk.main_quit()
