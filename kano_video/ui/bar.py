from gi.repository import Gtk, Gdk
import os
from shutil import rmtree

from kano_video.paths import image_dir
from kano_video.logic.playlist import playlistCollection
from kano_video.logic.youtube import tmp_dir

from .popup import LoadFilePopup, AddPlaylistPopup
from .general import KanoWidget, Spacer


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
        home_img.set_from_file(image_dir + '/icons/home.png')
        button = Gtk.Button()
        button.add(home_img)
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', self._switch_handler, 'home')
        button.set_alignment(0, 0)
        grid.attach(button, 0, 0, 1, 3)

        self._active_button = None

        button = Gtk.Button('LIBRARY')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.get_style_context().add_class('menu_link')
        button.connect('clicked', self._switch_handler, 'library')
        grid.attach(button, 1, 0, 1, 3)

        button = Gtk.Button('PLAYLISTS')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.get_style_context().add_class('menu_link')
        button.connect('clicked', self._switch_handler, 'playlist-collection')
        grid.attach(button, 2, 0, 1, 3)

        grid.attach(Spacer(), 3, 0, 1, 3)

        button = Gtk.Button('YOUTUBE')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.get_style_context().add_class('menu_link')
        button.connect('clicked', self._switch_handler, 'youtube')
        grid.attach(button, 4, 0, 1, 3)

        searchBar = SearchBar()
        grid.attach(searchBar, 5, 1, 1, 1)

        # Close button
        cross_icon = Gtk.Image()
        cross_icon.set_from_file(image_dir + '/icons/close.png')

        self._close_button = Gtk.Button()
        self._close_button.set_image(cross_icon)
        self._close_button.props.margin_right = 2
        self._close_button.set_can_focus(False)
        self._close_button.get_style_context().add_class('close')

        self._close_button.connect('clicked', self._close_button_click)
        self._close_button.connect('enter-notify-event',
                                   self._close_button_mouse_enter)
        self._close_button.connect('leave-notify-event',
                                   self._close_button_mouse_leave)

        grid.attach(self._close_button, 6, 0, 1, 3)

        self.add(grid)

    def _switch_handler(self, _button, switchto):
        if self._active_button:
            self._active_button.get_style_context().remove_class('active')
        self._active_button = _button
        _button.get_style_context().add_class('active')

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
        search_keyword_entry.connect('activate', self.switch_to_youtube,
                                     search_keyword_entry, False)
        self._grid.attach(search_keyword_entry, 0, 0, 1, 1)

        button = Gtk.Button('SEARCH')
        button.set_size_request(20, 20)
        button.connect('clicked', self.switch_to_youtube, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)

    def switch_to_youtube(self, _button, search_keyword=None, users=False):
        win = self.get_toplevel()
        win.switch_view('youtube', search_keyword=search_keyword, users=users)


class HorizontalBar(KanoWidget):
    left_widget = None
    centre_widget = None
    right_widget = None

    def __init__(self):
        super(HorizontalBar, self).__init__()

        self.get_style_context().add_class('bar')

        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(10)

        self._grid.attach(Gtk.Label(''), 0, 0, 1, 3)

        if self.left_widget:
            self._grid.attach(self.left_widget, 1, 1, 1, 1)
        else:
            self._grid.attach(Gtk.Label('', hexpand=True), 1, 0, 1, 3)

        if self.centre_widget:
            self._grid.attach(self.centre_widget, 2, 1, 1, 1)
        else:
            self._grid.attach(Gtk.Label('', hexpand=True), 2, 0, 1, 3)

        if self.right_widget:
            self._grid.attach(self.right_widget, 3, 1, 1, 1)
        else:
            self._grid.attach(Gtk.Label('', hexpand=True), 3, 0, 1, 3)

        self._grid.attach(Gtk.Label(''), 4, 0, 1, 3)


class AddVideoBar(HorizontalBar):

    def __init__(self):
        self.right_widget = Gtk.Button('ADD MEDIA')
        self.right_widget.get_style_context().add_class('green')
        self.right_widget.set_size_request(20, 20)
        self.right_widget.connect('clicked', self._add_handler)

        super(AddVideoBar, self).__init__()

    def _add_handler(self, _):
        popup = LoadFilePopup()
        print popup.run()


class PlayModeBar(HorizontalBar):

    def __init__(self, back_button=False):
        if back_button:
            self.left_widget = Gtk.Button('Back')
            self.left_widget.connect('clicked', self._back_handler)
            self.left_widget.set_alignment(0, 0.5)
            self.left_widget.get_style_context().add_class('grey')

        self.right_widget = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        grid = Gtk.Grid()
        self.right_widget.add(grid)

        fullscreen_str = 'PLAYER'
        fullscreen = Gtk.Label(fullscreen_str)
        fullscreen.set_size_request(70, 20)
        grid.attach(fullscreen, 0, 0, 1, 1)

        self._switch = Gtk.Switch()
        self._switch.set_size_request(20, 20)
        grid.attach(self._switch, 1, 0, 1, 1)

        windowed_str = 'FULLSCREEN'
        windowed = Gtk.Label(windowed_str)
        windowed.set_size_request(70, 20)
        grid.attach(windowed, 2, 0, 1, 1)

        super(PlayModeBar, self).__init__()

    def is_fullscreen(self):
        return self._switch.get_active()

    def _back_handler(self, _):
        win = self.get_toplevel()
        win.switch_view('previous')


class PlaylistAddBar(HorizontalBar):

    def __init__(self):
        self.right_widget = Gtk.Button('CREATE LIST')
        self.right_widget.get_style_context().add_class('green')
        self.right_widget.set_size_request(20, 20)
        self.right_widget.connect('clicked', self._add_handler)

        super(PlaylistAddBar, self).__init__()

    def _add_handler(self, button):
        popup = AddPlaylistPopup()
        res = popup.run()
        if res:
            win = self.get_toplevel()
            win.switch_view('playlist-collection')
