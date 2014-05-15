import os
from gi.repository import Gtk, Gdk, Pango

from kano.utils import list_dir

from .player import play_video, stop_videos
from .youtube import search_youtube_by_user, parse_youtube_entries, \
    search_youtube_by_keyword
from .icons import set_from_name
from .playlist import Playlist


class KanoWidget(Gtk.EventBox):

    def __init__(self):
        super(KanoWidget, self).__init__(hexpand=True)

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(10)
        self._grid.set_size_request(400, 30)

        self.add(self._grid)


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
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)
        Gdk.flush()

        Gtk.main_quit()


class MenuBar(Gtk.EventBox):
    _MENU_BAR_HEIGHT = 44
    _BUTTON_WIDTH = 150

    def __init__(self, home_cb, library_cb, playlists_cb, youtube_cb):
        Gtk.EventBox.__init__(self)

        self.get_style_context().add_class('menu_bar')

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_size_request(-1, self._MENU_BAR_HEIGHT)

        button = Gtk.Button('Home')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', home_cb)
        grid.attach(button, 0, 0, 1, 1)

        button = Gtk.Button('Library')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', library_cb)
        grid.attach(button, 1, 0, 1, 1)

        button = Gtk.Button('Playlists')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', playlists_cb)
        grid.attach(button, 2, 0, 1, 1)

        button = Gtk.Button('Youtube')
        button.set_size_request(self._BUTTON_WIDTH, self._MENU_BAR_HEIGHT)
        button.connect('clicked', youtube_cb)
        grid.attach(button, 3, 0, 1, 1)

        self.add(grid)


class Contents(Gtk.ScrolledWindow):

    def __init__(self, win):
        super(Contents, self).__init__(hexpand=True, vexpand=True)

        self.get_style_context().add_class('contents')

        self.props.margin_top = 20
        self.props.margin_bottom = 20
        self.props.margin_left = 20
        self.props.margin_right = 12

        self._current = None
        self._box = Gtk.Box(hexpand=True, vexpand=True)
        self.add_with_viewport(self._box)

        self._win = win

    def get_window(self):
        return self._win

    def set_contents(self, obj):
        for w in self._box.get_children():
            self._box.remove(w)

        obj.props.margin_right = 10
        Gtk.Container.add(self._box, obj)
        self._show_all(obj)

    def _show_all(self, w):
        w.show()
        if hasattr(w, '__iter__'):
            for c in w:
                self._show_all(c)


class VideoEntry(KanoWidget):

    def __init__(self, e):
        super(VideoEntry, self).__init__()

        row_height = 110
        row_title_height = 20
        row_desc_height = 15
        row_info_height = 15

        self._grid.set_size_request(-1, row_height)

        x_pos = 0

        button = Gtk.Button('Play')
        button.set_size_request(row_height, row_height)
        button.get_style_context().add_class('play')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'], False)
        self._grid.attach(button, x_pos, 0, 1, 3)
        x_pos += 1

        """
        button = Gtk.Button('FS')
        button.set_size_request(20, row_height)
        button.connect('clicked', play_video, e['video_url'], e['local_path'], True)
        self.attach(button, x_pos, 0, 1, 3)
        x_pos += 1
        """

        title_str = e['title'] if len(e['title']) <= 70 else e['title'][:67] + '...'
        label = Gtk.Label(title_str)
        label.set_size_request(-1, self._TITLE_HEIGHT)
        label.get_style_context().add_class('title')
        self._grid.attach(label, x_pos, 0, 1, 1)

        info_grid = Gtk.Grid()
        info_grid.set_size_request(-1, self._INFO_HEIGHT)
        info_grid.get_style_context().add_class('info')
        self._grid.attach(info_grid, x_pos, 2, 1, 1)

        if e['local_path'] is None:
            desc_str = e['description'] if len(e['description']) <= 70 else e['description'][:67] + '...'
            label = Gtk.Label(desc_str)
            label.set_size_request(-1, self._DESC_HEIGHT)
            self._grid.attach(label, x_pos, 1, 1, 1)

            duration_str = 'DURATION: {}:{}'.format(e['duration_min'], e['duration_sec'])
            label = Gtk.Label(duration_str)
            label.set_size_request(50, self._INFO_HEIGHT)
            info_grid.attach(label, 0, 0, 1, 1)

            info_grid.attach(Spacer(), 1, 0, 1, 1)

            viewcount_str = 'VIEWS: {}K'.format(int(e['viewcount'] / 1000.0))
            label = Gtk.Label(viewcount_str)
            label.set_size_request(50, self._INFO_HEIGHT)
            info_grid.attach(label, 2, 0, 1, 1)

            info_grid.attach(Spacer(), 3, 0, 1, 1)

            author_str = 'AUTHOR: {}'.format(e['author'])
            label = Gtk.Label(author_str)
            label.set_size_request(100, self._INFO_HEIGHT)
            info_grid.attach(label, 4, 0, 1, 1)

        button = Gtk.Button('Watch video')
        button.set_size_request(self._ENTRY_HEIGHT, self._INFO_HEIGHT)
        button.get_style_context().add_class('play')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'], False)
        info_grid.attach(button, 0, 1, 1, 1)

        info_grid.attach(Spacer(), 1, 1, 1, 1)

        button = Gtk.Button('Add to playlist')
        button.set_size_request(self._ENTRY_HEIGHT, self._INFO_HEIGHT)
        button.get_style_context().add_class('play')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'], False)
        info_grid.attach(button, 2, 1, 1, 1)

    def _play_handler(self, _button, _url, _localfile, _fullscreen):
        _button.set_label('Stop video')
        _button.get_style_context().add_class('playing')
        _button.disconnect(self._button_handler_id)
        self._button_handler_id = _button.connect('clicked', self._stop_handler, _url, _localfile, _fullscreen)
        Gtk.main_iteration()
        play_video(_button, _url, _localfile, _fullscreen)

    def _stop_handler(self, _button, _url, _localfile, _fullscreen):
        _button.set_label('Watch video')
        _button.get_style_context().remove_class('playing')
        _button.disconnect(self._button_handler_id)
        self._button_handler_id = _button.connect('clicked', self._play_handler, _url, _localfile, _fullscreen)
        Gtk.main_iteration()
        stop_videos(_button)


class VideoList(Gtk.EventBox):
    _LIST_HEIGHT = 400

    def __init__(self):
        super(VideoList, self).__init__()

        self.get_style_context().add_class('video_list')

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_size_request(-1, self._LIST_HEIGHT)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(self._grid)

        self.add(align)


class VideoListLocal(VideoList):

    def __init__(self, open_folder_dialog=False):
        super(VideoListLocal, self).__init__()

        self.get_style_context().add_class('video_list_local')

        if open_folder_dialog:
            local_dir = self.dir_dialog()
        else:
            local_dir = '/usr/share/kano-video/media/videos'

        files = list_dir(local_dir)
        files = [f for f in files if f[-3:] == 'mkv']
        print files

        if files:
            for i, f in enumerate(files):
                fullpath = os.path.join(local_dir, f)
                filename = os.path.splitext(f)[0]

                title_str = filename if len(filename) <= 40 else filename[:37] + '...'
                e = {'title': title_str,
                     'video_url': None,
                     'local_path': fullpath}

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i + 1, 1, 1)


class VideoListYoutube(VideoList):

    def __init__(self, keyword=None, username=None):
        super(VideoListYoutube, self).__init__()

        self.get_style_context().add_class('video_list_youtube')

        entries = None

        if keyword:
            entries = search_youtube_by_keyword(keyword)
            print 'searching by keyword: ' + keyword
        elif username:
            entries = search_youtube_by_user(username)
            print 'listing by username: ' + username
        else:
            entries = search_youtube_by_user('KanoComputing')
            print 'listing default videos by KanoComputing'

        if entries:
            parsed_entries = parse_youtube_entries(entries)
            for i, e in enumerate(parsed_entries):
                e['local_path'] = None

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i, 1, 1)


class SearchResultsBar(KanoWidget):

    def __init__(self, search_keyword, result_count):
        super(SearchResultsBar, self).__init__()

        self.get_style_context().add_class('search_results_bar')

        keyword_str = 'Showing results for "{}"'.format(search_keyword)
        keyword = Gtk.Label(keyword_str)
        keyword.set_size_request(100, 20)
        self._grid.attach(keyword, 0, 0, 1, 1)

        count_str = '{} videos'.format(result_count)
        count = Gtk.Label(count_str)
        keyword.set_size_request(100, 20)
        self._grid.attach(count, 0, 1, 1, 1)


class SearchBar(KanoWidget):

    def __init__(self, search_cb):
        super(SearchBar, self).__init__()

        self.get_style_context().add_class('search_bar')

        search_keyword_entry = Gtk.Entry()
        search_keyword_entry.props.placeholder_text = 'Search Youtube'
        search_keyword_entry.set_size_request(100, 20)
        self._grid.attach(search_keyword_entry, 0, 0, 1, 1)

        button = Gtk.Button('SEARCH')
        button.set_size_request(20, 20)
        button.connect('clicked', search_cb, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)

        button = Gtk.Button('SEARCH USERS')
        button.set_size_request(20, 20)
        button.connect('clicked', search_cb, search_keyword_entry, True)
        self._grid.attach(button, 3, 0, 1, 1)


class AddVideoBar(KanoWidget):

    def __init__(self):
        super(AddVideoBar, self).__init__()

        self.get_style_context().add_class('add_video_bar')

        title_str = 'Your library'
        title = Gtk.Label(title_str)
        title.get_style_context().add_class('title')
        title.set_alignment(0, 0.5)
        title.set_size_request(430, 20)
        self._grid.attach(title, 0, 0, 1, 1)

        button = Gtk.Button('ADD MEDIA')
        button.set_size_request(20, 20)
        # button.connect('clicked', search_cb, search_keyword_entry, False)
        self._grid.attach(button, 1, 0, 1, 1)


class PlayModeBar(KanoWidget):

    def __init__(self):
        super(PlayModeBar, self).__init__()

        self.get_style_context().add_class('play_mode_bar')

        title_str = 'Play mode'
        title = Gtk.Label(title_str)
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
