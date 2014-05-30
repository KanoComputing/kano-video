from gi.repository import Gtk

from kano_video.logic.playlist import playlistCollection

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

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
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

    def __init__(self, search_keyword=None, users=False):
        super(YoutubeView, self).__init__()

        if search_keyword and search_keyword.get_text():
            self._header = SearchResultsHeader(search_keyword.get_text(), '100,000')

            if users is False:
                self._list = VideoListYoutube(keyword=search_keyword.get_text())
            else:
                self._list = VideoListYoutube(username=search_keyword.get_text())
        else:
            self._header = YoutubeHeader()
            self._list = VideoListYoutube()

        self._grid.attach(self._header, 0, 0, 1, 1)
        self._grid.attach(self._list, 0, 2, 1, 1)

        self.play_mode = PlayModeBar()
        self._grid.attach(self.play_mode, 0, 1, 1, 1)


class DetailView(View):

    def __init__(self, video):
        super(DetailView, self).__init__()

        self.play_mode = PlayModeBar(back_button=True)
        self._grid.attach(self.play_mode, 0, 1, 1, 1)

        self._list = VideoDetailEntry(video)
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
                               playlist=playlist_name)
        self._grid.attach(self._vids, 0, 2, 1, 1)


class HomeView(View):

    def __init__(self):
        super(HomeView, self).__init__()

        self._popular = VideoListPopular()
        self._grid.attach(self._popular, 0, 0, 1, 1)


class NoInternetView(View):

    def __init__(self):
        super(NoInternetView, self).__init__()

        self._no_internet = Gtk.Label('Are you sure that you are connected to the internet?')
        self._no_internet.get_style_context().add_class('title')

        self._grid.attach(self._no_internet, 0, 0, 1, 1)
