from gi.repository import Gtk

from .general_ui import KanoWidget

from kano_video.logic.playlist import playlistCollection


class HeaderBar(KanoWidget):

    def __init__(self):
        super(HeaderBar, self).__init__()

        self.get_style_context().add_class('header_bar')

        title = Gtk.Label(self._title)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0)
        self._grid.attach(title, 0, 0, 1, 1)

        if self._count is not 1:
            self._item = '{}s'.format(self._item)
        title_str = '{} {}'.format(self._count, self._item)
        title = Gtk.Label(title_str)
        title.get_style_context().add_class('subtitle')
        title.set_alignment(0, 0)
        self._grid.attach(title, 0, 1, 1, 1)


class YoutubeHeader(HeaderBar):

    def __init__(self):
        self._title = 'Youtube'
        self._count = len(playlistCollection.collection)
        self._item = 'video'

        super(YoutubeHeader, self).__init__()

        self.get_style_context().add_class('youtube_bar')


class LibraryHeader(HeaderBar):

    def __init__(self):
        self._title = 'Library'
        self._count = len(playlistCollection.collection)
        self._item = 'video'

        super(LibraryHeader, self).__init__()

        self.get_style_context().add_class('library_bar')


class PlaylistCollectionHeader(HeaderBar):

    def __init__(self):
        self._title = 'Playlists'
        self._count = len(playlistCollection.collection)
        self._item = 'list'

        super(PlaylistCollectionHeader, self).__init__()

        self.get_style_context().add_class('playlist_collection_bar')


class PlaylistHeader(HeaderBar):

    def __init__(self, playlist):
        self._title = playlist.name
        self._count = len(playlist.playlist)
        self._item = 'video'

        super(PlaylistHeader, self).__init__()

        self.get_style_context().add_class('playlist_bar')


class SearchResultsHeader(HeaderBar):

    def __init__(self, search_keyword, result_count):
        self._title = 'Showing results for "{}"'.format(search_keyword)
        self._count = result_count
        self._item = 'video'

        super(SearchResultsHeader, self).__init__()

        self.get_style_context().add_class('search_results_bar')
