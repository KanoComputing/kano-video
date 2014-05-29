from gi.repository import Gtk, Gdk
import os
from shutil import rmtree

from kano_video.icons import set_from_name
from kano_video.logic.playlist import playlistCollection
from kano_video.logic.youtube import tmp_dir

from .popups import LoadFilePopup, AddPlaylistPopup
from .general_ui import KanoWidget, Spacer


class MenuBar(Gtk.EventBox):
    _MENU_BAR_HEIGHT = 66
    _BUTTON_WIDTH = 150

    def __init__(self):
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
        button.connect('clicked', self._switch_handler, 'home')
        button.set_alignment(0, 0)
        grid.attach(button, 0, 0, 1, 3)

        button = Gtk.Button('LIBRARY')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', self._switch_handler, 'library')
        grid.attach(button, 1, 0, 1, 3)

        button = Gtk.Button('PLAYLISTS')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', self._switch_handler, 'playlist-collection')
        grid.attach(button, 2, 0, 1, 3)

        grid.attach(Spacer(), 3, 0, 1, 3)

        button = Gtk.Button('YOUTUBE')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', self._switch_handler, 'youtube')
        grid.attach(button, 4, 0, 1, 3)

        searchBar = SearchBar()
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

    def _switch_handler(self, _button, switchto):
        win = self.get_toplevel()
        win.switch_view(switchto)

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

    def __init__(self):
        super(SearchBar, self).__init__()

        self.get_style_context().add_class('search_bar')
        self._grid.set_column_spacing(10)

        search_keyword_entry = Gtk.Entry(hexpand=True)
        search_keyword_entry.props.placeholder_text = 'Search Youtube'
        search_keyword_entry.set_alignment(0)
        search_keyword_entry.set_size_request(100, 20)
        self._grid.attach(search_keyword_entry, 0, 0, 1, 1)

        button = Gtk.Button('SEARCH')
        button.set_size_request(20, 20)
        button.connect('clicked', self.switch_to_youtube, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)

    def switch_to_youtube(self, _button, search_keyword=None, users=False):
        win = self.get_toplevel()
        win.switch_view('youtube', search_keyword=search_keyword, users=users)


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
        button.connect('clicked', self._add_handler)
        self._grid.attach(button, 1, 0, 1, 1)

    def _add_handler(self, _):
        popup = LoadFilePopup()
        print popup.run()


class PlayModeBar(KanoWidget):

    def __init__(self, back_button=False):
        super(PlayModeBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('play_mode_bar')

        if back_button:
            button = Gtk.Button('Back')
            button.connect('clicked', self._back_handler)
            button.set_alignment(0, 0.5)
            self._grid.attach(button, 0, 0, 1, 1)

        title_str = ''
        title = Gtk.Label(title_str, hexpand=True)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        self._grid.attach(title, 1, 0, 1, 1)

        fullscreen_str = 'PLAYER'
        fullscreen = Gtk.Label(fullscreen_str)
        fullscreen.set_size_request(70, 20)
        self._grid.attach(fullscreen, 2, 0, 1, 1)

        self._switch = Gtk.Switch()
        self._switch.set_size_request(20, 20)
        self._grid.attach(self._switch, 3, 0, 1, 1)

        windowed_str = 'FULLSCREEN'
        windowed = Gtk.Label(windowed_str)
        windowed.set_size_request(70, 20)
        self._grid.attach(windowed, 4, 0, 1, 1)

    def is_fullscreen(self):
        return self._switch.get_active()

    def _back_handler(self, _):
        win = self.get_toplevel()
        win.switch_view('previous')


class PlaylistAddBar(KanoWidget):

    def __init__(self):
        super(PlaylistAddBar, self).__init__()

        self.get_style_context().add_class('bar')
        self.get_style_context().add_class('playlist_add_bar')

        title_str = ''
        title = Gtk.Label(title_str, hexpand=True)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(430, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        button = Gtk.Button('CREATE LIST')
        button.get_style_context().add_class('green')
        button.set_size_request(20, 20)
        button.connect('clicked', self._add_handler)
        self._grid.attach(button, 1, 0, 1, 1)

    def _add_handler(self, button):
        popup = AddPlaylistPopup()
        res = popup.run()
        if res:
            win = self.get_toplevel()
            win.switch_view('playlist-collection')
