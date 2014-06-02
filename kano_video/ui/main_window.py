#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from gi.repository import Gtk, Gdk

from kano.network import is_internet
from kano_video.logic.playlist import playlistCollection

from .general import Contents
from .bar import MenuBar
from .view import HomeView, LocalView, YoutubeView, \
    PlaylistView, PlaylistCollectionView, DetailView, \
    NoInternetView


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

        self.view = HomeView()
        self.prev_view = []

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
                 'no-internet': self.switch_to_no_internet,
                 'previous': self.switch_to_previous}

        if view is 'playlist':
            views[view](playlist)
        elif view is 'youtube':
            views[view](search_keyword=search_keyword, users=users)
        elif view is 'detail':
            views[view](video=video, playlist_name=playlist)
        else:
            views[view]()

    def switch_to_home(self):
        self.prev_view = []

        self.view = HomeView()
        self.contents.set_contents(self.view)

    def switch_to_playlist_collection(self):
        self.prev_view = []

        self.view = PlaylistCollectionView()
        self.contents.set_contents(self.view)

    def switch_to_playlist(self, playlist):
        self.prev_view.append(self.view)

        self.view = PlaylistView(playlist)
        self.contents.set_contents(self.view)

    def switch_to_youtube(self, search_keyword=None, users=False):
        if is_internet():
            cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
            self.get_root_window().set_cursor(cursor)

            Gtk.main_iteration_do(True)

            self.prev_view = []

            self.view = YoutubeView(search_keyword, users)
            self.contents.set_contents(self.view)

            cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
            self.get_root_window().set_cursor(cursor)
        else:
            self.switch_view('no-internet')

    def switch_to_local(self):
        self.prev_view = []

        self.view = LocalView()
        self.contents.set_contents(self.view)

    def switch_to_detail(self, video, playlist_name=None):
        self.prev_view.append(self.view)

        self.view = DetailView(video, playlist_name=playlist_name)
        self.contents.set_contents(self.view)

    def switch_to_no_internet(self):
        self.prev_view = []

        self.view = NoInternetView()
        self.contents.set_contents(self.view)

    def switch_to_previous(self):
        prev = self.prev_view.pop()
        if prev:
            self.view = prev
            self.contents.set_contents(self.view)

    def on_close(self, widget=None, event=None):
        playlistCollection.save()
        Gtk.main_quit()
