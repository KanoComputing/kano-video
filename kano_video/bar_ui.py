from gi.repository import Gtk, Gdk, Pango
import os
from shutil import rmtree

from .icons import set_from_name
from .playlist import playlistCollection
from .youtube import tmp_dir

from .general_ui import KanoWidget, Spacer


class TopBar(Gtk.EventBox):
    _TOP_BAR_HEIGHT = 44

    def __init__(self, title):
        super(TopBar, self).__init__(hexpand=True, vexpand=True)

        self.get_style_context().add_class('top_bar_container')

        box = Gtk.Box()
        box.set_size_request(-1, self._TOP_BAR_HEIGHT)

        self._header = Gtk.Label(title, halign=Gtk.Align.CENTER,
                                 valign=Gtk.Align.CENTER,
                                 hexpand=True)
        box.pack_start(self._header, True, True, 0)

        self._header.modify_font(Pango.FontDescription('Bariol 13'))
        self._header.get_style_context().add_class('header')

        # Close button
        cross_icon = set_from_name('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')
        self._close_button.get_style_context().add_class('no_border')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        box.pack_start(self._close_button, False, False, 0)

        self.add(box)

    def _close_button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _close_button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _close_button_click(self, event):
        self.get_toplevel().destroy()


class MenuBar(Gtk.EventBox):
    _MENU_BAR_HEIGHT = 66
    _BUTTON_WIDTH = 150

    def __init__(self, home_cb, library_cb, playlists_cb,
                 youtube_cb, search_cb):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class('menu_bar')

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_size_request(-1, self._MENU_BAR_HEIGHT)

        home_img = Gtk.Image()
        home_img.set_from_file('media/images/icons/home.png')
        button = Gtk.Button()
        button.add(home_img)
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', home_cb)
        grid.attach(button, 0, 0, 1, 3)

        button = Gtk.Button('LIBRARY')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', library_cb)
        grid.attach(button, 1, 0, 1, 3)

        button = Gtk.Button('PLAYLISTS')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', playlists_cb)
        grid.attach(button, 2, 0, 1, 3)

        grid.attach(Spacer(), 3, 0, 1, 3)

        button = Gtk.Button('YOUTUBE')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', youtube_cb)
        grid.attach(button, 4, 0, 1, 3)

        searchBar = SearchBar(search_cb)
        grid.attach(searchBar, 5, 1, 1, 1)

        # Close button
        cross_icon = set_from_name('cross')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('top_bar_button')
        self._close_button.get_style_context().add_class('no_border')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        grid.attach(self._close_button, 6, 0, 1, 3)

        self.add(grid)

    def _close_button_mouse_enter(self, button, event):
        # Change the cursor to hour Glass
        cursor = Gdk.Cursor.new(Gdk.CursorType.HAND1)
        self.get_root_window().set_cursor(cursor)

    def _close_button_mouse_leave(self, button, event):
        # Set the cursor to normal Arrow
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def _close_button_click(self, event):
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        # Remove temp files
        if os.path.exists(tmp_dir):
            rmtree(tmp_dir)

        playlistCollection.save()

        Gtk.main_quit()


class SearchBar(KanoWidget):

    def __init__(self, search_cb):
        super(SearchBar, self).__init__()

        self.get_style_context().add_class('search_bar')

        search_keyword_entry = Gtk.Entry(hexpand=True)
        search_keyword_entry.props.placeholder_text = 'Search Youtube'
        search_keyword_entry.set_alignment(0.5)
        search_keyword_entry.set_size_request(100, 20)
        self._grid.attach(search_keyword_entry, 0, 0, 1, 1)

        button = Gtk.Button('SEARCH')
        button.set_size_request(20, 20)
        button.connect('clicked', search_cb, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)

        """
        button = Gtk.Button('SEARCH USERS')
        button.set_size_request(20, 20)
        button.connect('clicked', search_cb, search_keyword_entry, True)
        self._grid.attach(button, 3, 0, 1, 1)
        """


class AddVideoBar(KanoWidget):

    def __init__(self):
        super(AddVideoBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('add_video_bar')

        title_str = 'Your library'
        title = Gtk.Label(title_str, hexpand=True)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(430, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        button = Gtk.Button('ADD MEDIA')
        button.get_style_context().add_class('green')
        button.set_size_request(20, 20)
        # button.connect('clicked', search_cb, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)


class PlayModeBar(KanoWidget):

    def __init__(self):
        super(PlayModeBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('play_mode_bar')

        title_str = 'Play mode'
        title = Gtk.Label(title_str, hexpand=True)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(310, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        fullscreen_str = 'Fullscreen'
        fullscreen = Gtk.Label(fullscreen_str)
        fullscreen.set_size_request(70, 20)
        self._grid.attach(fullscreen, 1, 0, 1, 1)

        self._switch = Gtk.Switch()
        self._switch.set_size_request(20, 20)
        self._grid.attach(self._switch, 2, 0, 1, 1)

        windowed_str = 'In player'
        windowed = Gtk.Label(windowed_str)
        windowed.set_size_request(70, 20)
        self._grid.attach(windowed, 4, 0, 1, 1)

    def is_fullscreen(self):
        return not self._switch.get_active()


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


class YoutubeBar(HeaderBar):

    def __init__(self):
        self._title = 'Youtube'
        self._count = len(playlistCollection.collection)
        self._item = 'video'

        super(YoutubeBar, self).__init__()

        self.get_style_context().add_class('youtube_bar')


class LibraryBar(HeaderBar):

    def __init__(self):
        self._title = 'Library'
        self._count = len(playlistCollection.collection)
        self._item = 'video'

        super(LibraryBar, self).__init__()

        self.get_style_context().add_class('library_bar')


class PlaylistCollectionBar(HeaderBar):

    def __init__(self):
        self._title = 'Playlists'
        self._count = len(playlistCollection.collection)
        self._item = 'list'

        super(PlaylistCollectionBar, self).__init__()

        self.get_style_context().add_class('playlist_collection_bar')


class PlaylistBar(HeaderBar):

    def __init__(self, playlist):
        self._title = playlist.name
        self._count = len(playlist.playlist)
        self._item = 'video'

        super(PlaylistBar, self).__init__()

        self.get_style_context().add_class('playlist_bar')


class SearchResultsBar(HeaderBar):

    def __init__(self, search_keyword, result_count):
        self._title = 'Showing results for "{}"'.format(search_keyword)
        self._count = result_count
        self._item = 'video'

        super(SearchResultsBar, self).__init__()

        self.get_style_context().add_class('search_results_bar')
