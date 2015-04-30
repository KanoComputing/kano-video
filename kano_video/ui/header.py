# header.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Header widgets for views
#


from gi.repository import Gtk

from .general import KanoWidget

from kano_video.logic.playlist import playlistCollection, \
    library_playlist


class HeaderBar(KanoWidget):
    """
    Base header bar for subclassing
    """

    def __init__(self):
        super(HeaderBar, self).__init__()

        self.get_style_context().add_class('header_bar')

        title = Gtk.Label(self._title)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0)
        self._grid.attach(title, 0, 0, 1, 1)

        if self._count is not 1:
            self._item = '{}s'.format(self._item)
        title_str = self._item.format(self._count)
        title = Gtk.Label(title_str)
        title.get_style_context().add_class('subtitle')
        title.set_alignment(0, 0)
        self._grid.attach(title, 0, 1, 1, 1)


class YoutubeHeader(HeaderBar):
    """
    Header bar for views of YouTube videos
    """

    def __init__(self):
        self._title = 'YouTube'
        self._count = 10
        self._item = '{} video'

        super(YoutubeHeader, self).__init__()

        self.get_style_context().add_class('youtube_bar')


class LibraryHeader(HeaderBar):
    """
    Header bar for views of local videos
    """

    def __init__(self):
        self._title = 'Library'
        self._count = len(library_playlist.playlist)
        self._item = '{} video'

        super(LibraryHeader, self).__init__()

        self.get_style_context().add_class('library_bar')


class PlaylistCollectionHeader(HeaderBar):
    """
    Header bar for views of playlist collections
    """

    def __init__(self):
        self._title = 'Playlists'
        self._count = len(playlistCollection.collection)
        self._item = '{} list'

        super(PlaylistCollectionHeader, self).__init__()

        self.get_style_context().add_class('playlist_collection_bar')


class PlaylistHeader(HeaderBar):
    """
    Header bar for views of playlists
    """

    def __init__(self, playlist):
        self._title = playlist.name
        self._count = len(playlist.playlist)
        self._item = '{} video'

        super(PlaylistHeader, self).__init__()

        self.get_style_context().add_class('playlist_bar')


class SearchResultsHeader(HeaderBar):
    """
    Header bar for views of searched YouTube videos
    """

    def __init__(self, search_keyword, result_count, start=1):
        self._title = 'Showing results for "{}"'.format(search_keyword)
        if result_count == 1000000:
            self._item = 'Results {} - {} of many video'.format(start, start + 9)
            self._count = ''
        else:
            self._item = 'Results {} - {} of {} video'.format(start, start + 9, '{}')
            self._count = result_count

        super(SearchResultsHeader, self).__init__()

        self.get_style_context().add_class('search_results_bar')
