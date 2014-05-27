from gi.repository import Gtk

from .bar_ui import TopBar, SearchResultsBar, \
    AddVideoBar, PlayModeBar, LibraryBar, PlaylistBar, \
    PlaylistCollectionBar, YoutubeBar
from .video_ui import VideoList, VideoListLocal, \
    VideoListYoutube, VideoListPopular
from .playlist_ui import PlaylistList, PlaylistAddBar
from .playlist import playlistCollection


class View(Gtk.EventBox):
    _VIEW_HEIGHT = 400

    def __init__(self):
        super(View, self).__init__()

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_size_request(-1, self._VIEW_HEIGHT)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(self._grid)

        self.add(align)


class LocalView(View):

    def __init__(self):
        super(LocalView, self).__init__()

        self._header = LibraryBar()
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._add = AddVideoBar()
        self._grid.attach(self._add, 0, 1, 1, 1)

        self._play_mode = PlayModeBar()
        self._grid.attach(self._play_mode, 0, 2, 1, 1)

        self._list = VideoListLocal()
        self._grid.attach(self._list, 0, 3, 1, 1)


class YoutubeView(View):

    def __init__(self):
        super(YoutubeView, self).__init__()

        self._header = YoutubeBar()
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._play_mode = PlayModeBar()
        self._grid.attach(self._play_mode, 0, 1, 1, 1)

    def search_handler(self, _button, search_keyword=None, users=False):
        self._grid.remove(self._header)

        try:
            self._grid.remove(self._list)
        except Exception:
            pass

        if search_keyword and search_keyword.get_text():
            self._header = SearchResultsBar(search_keyword.get_text(), '100,000')

            if users is False:
                self._list = VideoListYoutube(keyword=search_keyword.get_text())
            else:
                self._list = VideoListYoutube(username=search_keyword.get_text())
        else:
            self._header = YoutubeBar()
            self._list = VideoListYoutube()

        self._grid.attach(self._header, 0, 0, 1, 1)
        self._grid.attach(self._list, 0, 2, 1, 1)
        self._grid.show_all()


class PlaylistCollectionView(View):

    def __init__(self, playlist_cb):
        super(PlaylistCollectionView, self).__init__()

        self._header = PlaylistCollectionBar()
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._add = PlaylistAddBar()
        self._grid.attach(self._add, 0, 1, 1, 1)

        self._vids = PlaylistList(playlistCollection.collection, playlist_cb)
        self._grid.attach(self._vids, 0, 2, 1, 1)


class PlaylistView(View):

    def __init__(self, playlist_name):
        super(PlaylistView, self).__init__()

        playlist = playlistCollection.collection[playlist_name]
        self._header = PlaylistBar(playlist)
        self._grid.attach(self._header, 0, 0, 1, 1)

        self._vids = VideoList(videos=playlist.playlist)
        self._grid.attach(self._vids, 0, 1, 1, 1)


class HomeView(View):

    def __init__(self):
        super(HomeView, self).__init__()

        self._popular = VideoListPopular()
        self._grid.attach(self._popular, 0, 0, 1, 1)
