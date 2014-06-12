# view.py
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# 


from gi.repository import Gtk

from kano_video.logic.playlist import playlistCollection
from kano_video.logic.youtube import page_to_index, get_last_search_count

from .header import SearchResultsHeader, \
    LibraryHeader, PlaylistHeader, \
    PlaylistCollectionHeader, YoutubeHeader
from .bar import AddVideoBar, PlayModeBar, \
    PlaylistAddBar
from .video import VideoList, VideoListLocal, \
    VideoListYoutube, VideoListPopular, \
    VideoDetailEntry
from .playlist import PlaylistList


class View(Gtk.EventBox):
    _VIEW_WIDTH = 750
    _VIEW_HEIGHT = 400

    def __init__(self):
        super(View, self).__init__()

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(0)
        self._grid.set_size_request(self._VIEW_WIDTH, self._VIEW_HEIGHT)

        align = Gtk.Alignment(xalign=0.5, yalign=0, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(self._grid)

        self.add(align)


class LocalView(View):

    def __init__(self):
        super(LocalView, self).__init__()

        self._header = LibraryHeader()
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._add = AddVideoBar()
        self._grid.attach(self._add, 0, 1, 1, 1)

        self.play_mode = PlayModeBar()
        self._grid.attach(self.play_mode, 0, 2, 1, 1)

        self._list = VideoListLocal()
        self._grid.attach(self._list, 0, 3, 1, 1)


class YoutubeView(View):

    def __init__(self, search_keyword=None, users=False, page=1):
        super(YoutubeView, self).__init__()

        if search_keyword and search_keyword.get_text():
            index = page_to_index(page)

            if users is False:
                self._list = VideoListYoutube(keyword=search_keyword.get_text(), page=page)
            else:
                self._list = VideoListYoutube(username=search_keyword.get_text())

            self._header = SearchResultsHeader(search_keyword.get_text(), get_last_search_count(), start=index)
        else:
            self._header = YoutubeHeader()
            self._list = VideoListYoutube(page=page)

        self._grid.attach(self._header, 0, 0, 1, 1)
        self._grid.attach(self._list, 0, 2, 1, 1)

        self.play_mode = PlayModeBar()
        self._grid.attach(self.play_mode, 0, 1, 1, 1)

        if search_keyword and search_keyword.get_text() is not '':
            navigation_grid = Gtk.Grid()
            self._grid.attach(navigation_grid, 0, 3, 1, 1)

            prev_button = Gtk.Button('Back')
            prev_button.get_style_context().add_class('green')
            prev_button.connect('clicked', self._switch_page, page - 1, search_keyword)
            navigation_grid.attach(prev_button, 0, 0, 1, 1)
            if page == 1:
                prev_button.set_sensitive(False)

            navigation_grid.attach(Gtk.Label('', hexpand=True), 1, 0, 1, 1)

            next_button = Gtk.Button('Next')
            next_button.get_style_context().add_class('green')
            next_button.connect('clicked', self._switch_page, page + 1, search_keyword)
            navigation_grid.attach(next_button, 2, 0, 1, 1)

    def _switch_page(self, _, page, search_keyword=None):
        win = self.get_toplevel()
        win.switch_view('youtube', search_keyword=search_keyword, page=page)


class DetailView(View):

    def __init__(self, video, playlist_name=None):
        super(DetailView, self).__init__()

        self.play_mode = PlayModeBar(back_button=True)
        self._grid.attach(self.play_mode, 0, 1, 1, 1)

        self._list = VideoDetailEntry(video, playlist_name=playlist_name)
        self._grid.attach(self._list, 0, 2, 1, 1)


class PlaylistCollectionView(View):

    def __init__(self):
        super(PlaylistCollectionView, self).__init__()

        self._header = PlaylistCollectionHeader()
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._add = PlaylistAddBar()
        self._grid.attach(self._add, 0, 1, 1, 1)

        self._vids = PlaylistList(playlistCollection.collection)
        self._grid.attach(self._vids, 0, 2, 1, 1)


class PlaylistView(View):

    def __init__(self, playlist_name):
        super(PlaylistView, self).__init__()

        playlist = playlistCollection.collection[playlist_name]
        self._header = PlaylistHeader(playlist)
        self._grid.attach(self._header, 0, 0, 1, 1)

        self.play_mode = PlayModeBar(back_button=True)
        self._grid.attach(self.play_mode, 0, 1, 1, 1)

        self._vids = VideoList(videos=playlist.playlist,
                               playlist=playlist_name,
                               permanent=playlist.permanent)
        self._grid.attach(self._vids, 0, 2, 1, 1)


class HomeView(View):

    def __init__(self):
        super(HomeView, self).__init__()

        title = Gtk.Label('Popular on Youtube')
        title.set_alignment(0, 0.5)
        title.get_style_context().add_class('title')
        self._grid.attach(title, 0, 0, 1, 1)

        self._popular = VideoListPopular()
        self._grid.attach(self._popular, 0, 1, 1, 1)


class NoInternetView(View):

    def __init__(self):
        super(NoInternetView, self).__init__()

        self._no_internet = Gtk.Label('Are you sure that you are connected to the internet?')
        self._no_internet.get_style_context().add_class('title')

        self._grid.attach(self._no_internet, 0, 0, 1, 1)
