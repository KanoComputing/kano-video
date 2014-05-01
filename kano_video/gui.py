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
        self.grid.attach(self.video_list, 0, 2, 1, 1)

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

        row_height = 30

        if open_folder_dialog:
            local_dir = self.dir_dialog()
        else:
            local_dir = '/usr/share/kano-video/media'

        files = list_dir(local_dir)
        files = [f for f in files if f[-3:] == 'mkv']
        print files

        if files:
            for i, f in enumerate(files):
                fullpath = os.path.join(local_dir, f)
                filename = os.path.splitext(f)[0]

                x_pos = 0

                button = Gtk.Button('Play')
                button.set_size_request(50, row_height)
                button.connect('clicked', play_video, None, fullpath, False)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                button = Gtk.Button('FS')
                button.set_size_request(20, row_height)
                button.connect('clicked', play_video, None, fullpath, True)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                button = Gtk.Button('Stop')
                button.set_size_request(20, row_height)
                button.connect('clicked', stop_videos)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                title_str = filename if len(filename) <= 40 else filename[:37] + '...'
                label = Gtk.Label(title_str)
                label.set_size_request(400, row_height)
                grid.attach(label, x_pos, i, 1, 1)
                x_pos += 1

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        padding = 20
        align.set_padding(padding, padding, padding, padding)
        align.add(grid)
        return align

    def video_list_youtube(self, keyword=None, username=None):
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_size_request(400, 400)

        row_height = 30
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
                # author
                # description
                # duration, duration_min, duration_sec
                # title
                # video_url
                # viewcount

                x_pos = 0

                button = Gtk.Button('Play')
                button.set_size_request(50, row_height)
                button.connect('clicked', play_video, e['video_url'], None, False)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                button = Gtk.Button('FS')
                button.set_size_request(20, row_height)
                button.connect('clicked', play_video, e['video_url'], None, True)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                button = Gtk.Button('Stop')
                button.set_size_request(20, row_height)
                button.connect('clicked', stop_videos)
                grid.attach(button, x_pos, i, 1, 1)
                x_pos += 1

                title_str = e['title'] if len(e['title']) <= 40 else e['title'][:37] + '...'
                label = Gtk.Label(title_str)
                label.set_size_request(400, row_height)
                grid.attach(label, x_pos, i, 1, 1)
                x_pos += 1

                duration_str = '{}:{}'.format(e['duration_min'], e['duration_sec'])
                label = Gtk.Label(duration_str)
                label.set_size_request(50, row_height)
                grid.attach(label, x_pos, i, 1, 1)
                x_pos += 1

                viewcount_str = '{}k'.format(int(e['viewcount'] / 1000.0))
                label = Gtk.Label(viewcount_str)
                label.set_size_request(50, row_height)
                grid.attach(label, x_pos, i, 1, 1)
                x_pos += 1

                label = Gtk.Label(e['author'])
                label.set_size_request(100, row_height)
                grid.attach(label, x_pos, i, 1, 1)

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
