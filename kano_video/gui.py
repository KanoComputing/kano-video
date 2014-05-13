#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
from gi.repository import Gtk

from kano.utils import list_dir
from kano.network import is_internet

from .youtube import search_youtube_by_user, parse_youtube_entries, \
    search_youtube_by_keyword
from .icons import set_from_name
from .player import play_video, stop_videos


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='Kano Video')

        self._win_width = 600
        self._contents_height = 400

        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        top_bar = self.make_top_bar('Kano Video')
        self.grid.attach(top_bar, 0, 0, 1, 1)

        search_bar = self.make_search_bar()
        self.grid.attach(search_bar, 0, 1, 1, 1)

        if is_internet():
            self.video_list = self.video_list_youtube()
        else:
            self.video_list = self.video_list_local()
        self.contents = Contents(self.grid)
        self.contents.set_contents(self.video_list)
        self.contents.set_size_request(self._win_width, self._contents_height)

        self.grid.attach(self.contents, 0, 2, 1, 1)

    def make_top_bar(self, title):
        height = 44

        eb = Gtk.EventBox()
        eb.get_style_context().add_class('top_bar_container')

        header = Gtk.Label(title)
        header.set_size_request(400, height)
        header.get_style_context().add_class('header')

        cross = set_from_name('cross')

        close_button = Gtk.Button()
        close_button.set_image(cross)
        close_button.set_size_request(height, height)
        close_button.set_can_focus(False)
        close_button.get_style_context().add_class("top_bar_button")
        close_button.connect('clicked', Gtk.main_quit)

        grid = Gtk.Grid()
        grid.attach(header, 0, 0, 1, 1)
        grid.attach(close_button, 1, 0, 1, 1)
        grid.set_size_request(0, height)

        eb.add(grid)
        return eb

    def make_search_bar(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_size_request(400, 30)

        search_keyword_entry = Gtk.Entry()
        search_keyword_entry.props.placeholder_text = 'Search Youtube'
        search_keyword_entry.set_size_request(100, 20)
        grid.attach(search_keyword_entry, 0, 0, 1, 1)

        button = Gtk.Button('Search')
        button.set_size_request(20, 20)
        button.connect('clicked', self.search, search_keyword_entry, None)
        grid.attach(button, 1, 0, 1, 1)

        list_by_username = Gtk.Entry()
        list_by_username.props.placeholder_text = 'List by username'
        list_by_username.set_size_request(100, 20)
        grid.attach(list_by_username, 2, 0, 1, 1)

        button = Gtk.Button('List')
        button.set_size_request(20, 20)
        button.connect('clicked', self.search, None, list_by_username)
        grid.attach(button, 3, 0, 1, 1)

        button = Gtk.Button('Local media')
        button.set_size_request(20, 20)
        button.connect('clicked', self.list_local, False)
        grid.attach(button, 4, 0, 1, 1)

        button = Gtk.Button('Open dir...')
        button.set_size_request(20, 20)
        button.connect('clicked', self.list_local, True)
        grid.attach(button, 5, 0, 1, 1)
        return grid

    def search(self, _button, search_keyword_entry=None, list_by_username=None):
        if search_keyword_entry and search_keyword_entry.get_text():
            self.grid.remove(self.video_list)
            self.video_list = self.video_list_youtube(keyword=search_keyword_entry.get_text())
            self.grid.attach(self.video_list, 0, 2, 1, 1)
            self.show_all()

        elif list_by_username and list_by_username.get_text():
            self.grid.remove(self.video_list)
            self.video_list = self.video_list_youtube(username=list_by_username.get_text())
            self.grid.attach(self.video_list, 0, 2, 1, 1)
            self.show_all()

    def list_local(self, _button, open_folder_dialog=False):
        self.grid.remove(self.video_list)
        self.video_list = self.video_list_local(open_folder_dialog)
        self.grid.attach(self.video_list, 0, 2, 1, 1)
        self.show_all()

    def video_list_local(self, open_folder_dialog=False):
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_size_request(400, 400)

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

                entry_grid = VideoEntry(e, True)
                grid.attach(entry_grid, 0, i, 1, 1)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(grid)
        return align

    def video_list_youtube(self, keyword=None, username=None):
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_size_request(400, 400)

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

                entry_grid = VideoEntry(e, False)
                grid.attach(entry_grid, 0, i, 1, 1)

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(grid)
        return align

    def dir_dialog(self):
        dialog = Gtk.FileChooserDialog(
            "Please select a folder", self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)

        # Set up file filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Video files")
        filter_text.add_pattern('*.mkv')
        dialog.add_filter(filter_text)

        dialog.set_current_folder(os.path.expanduser('~'))

        response = dialog.run()

        dir_path = None
        if response == Gtk.ResponseType.OK:
            dir_path = dialog.get_filename()
        dialog.destroy()
        return dir_path


class VideoEntry(Gtk.EventBox):

    def __init__(self, e, local=False):
        Gtk.EventBox.__init__(self)

        row_height = 110
        row_title_height = 20
        row_desc_height = 15
        row_info_height = 15

        entry_grid = Gtk.Grid()
        self.add(entry_grid)

        entry_grid.set_size_request(400, row_height)

        x_pos = 0

        button = Gtk.Button('Play')
        button.set_size_request(row_height, row_height)
        button.get_style_context().add_class('play')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'], False)
        entry_grid.attach(button, x_pos, 0, 1, 3)
        x_pos += 1

        """
        button = Gtk.Button('FS')
        button.set_size_request(20, row_height)
        button.connect('clicked', play_video, e['video_url'], e['local_path'], True)
        self.attach(button, x_pos, 0, 1, 3)
        x_pos += 1
        """

        title_str = e['title'] if len(e['title']) <= 150 else e['title'][:147] + '...'
        label = Gtk.Label(title_str)
        label.set_size_request(400, row_title_height)
        label.get_style_context().add_class('title')
        entry_grid.attach(label, x_pos, 0, 1, 1)

        if local is False:
            desc_str = e['description'] if len(e['description']) <= 150 else e['description'][:37] + '...'
            label = Gtk.Label(desc_str)
            label.set_size_request(400, row_desc_height)
            entry_grid.attach(label, x_pos, 1, 1, 1)

            info_grid = Gtk.Grid()
            info_grid.set_size_request(400, row_info_height)
            info_grid.get_style_context().add_class('info')
            entry_grid.attach(info_grid, x_pos, 2, 1, 1)

            duration_str = 'DURATION: {}:{} |'.format(e['duration_min'], e['duration_sec'])
            label = Gtk.Label(duration_str)
            label.set_size_request(50, row_info_height)
            info_grid.attach(label, 0, 0, 1, 1)

            viewcount_str = 'VIEWS: {}K |'.format(int(e['viewcount'] / 1000.0))
            label = Gtk.Label(viewcount_str)
            label.set_size_request(50, row_info_height)
            info_grid.attach(label, 1, 0, 1, 1)

            author_str = 'AUTHOR: {}'.format(e['author'])
            label = Gtk.Label(author_str)
            label.set_size_request(100, row_height)
            info_grid.attach(label, 2, 0, 1, 1)

    def _play_handler(self, _button, _url, _localfile, _fullscreen):
        _button.set_label('Stop')
        _button.get_style_context().add_class('playing')
        _button.disconnect(self._button_handler_id)
        self._button_handler_id = _button.connect('clicked', self._stop_handler, _url, _localfile, _fullscreen)
        Gtk.main_iteration()
        play_video(_button, _url, _localfile, _fullscreen)

    def _stop_handler(self, _button, _url, _localfile, _fullscreen):
        _button.set_label('Play')
        _button.get_style_context().remove_class('playing')
        _button.disconnect(self._button_handler_id)
        self._button_handler_id = _button.connect('clicked', self._play_handler, _url, _localfile, _fullscreen)
        Gtk.main_iteration()
        stop_videos(_button)


class Contents(Gtk.ScrolledWindow):

    def __init__(self, win):
        Gtk.ScrolledWindow.__init__(self, hexpand=True, vexpand=True)
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
