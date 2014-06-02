import os
from gi.repository import Gtk, Gdk
from urllib import urlretrieve
from time import time

from kano.utils import list_dir
from kano.gtk3.kano_dialog import KanoDialog

from kano_video.logic.player import play_video
from kano_video.logic.youtube import search_youtube_by_user, \
    parse_youtube_entries, search_youtube_by_keyword, tmp_dir
from kano_video.logic.playlist import playlistCollection

from .popup import AddToPlaylistPopup
from .general import Spacer


class VideoEntry(Gtk.Button):
    _ENTRY_HEIGHT = 110
    _TITLE_HEIGHT = 20
    _DESC_HEIGHT = 15
    _INFO_HEIGHT = 15

    def __init__(self, e, playlist_name=None):
        super(VideoEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        self.connect('clicked', self._detail_view_handler, e, playlist_name)

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(30)
        self.add(button_grid)

        if e['thumbnail']:
            img = Gtk.Image()

            thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())
            urlretrieve(e['thumbnail'], thumbnail)
            img.set_from_file(thumbnail)
        else:
            img = Gtk.EventBox()
        img.set_size_request(self._ENTRY_HEIGHT, self._ENTRY_HEIGHT)
        img.get_style_context().add_class('thumb')
        button_grid.attach(img, 0, 0, 1, 4)

        title_str = e['title'] if len(e['title']) <= 70 else e['title'][:67] + '...'
        label = Gtk.Label(title_str, hexpand=True)
        label.set_alignment(0, 0.5)
        label.get_style_context().add_class('title')
        button_grid.attach(label, 1, 0, 1, 1)

        if playlist_name:
            remove = Gtk.Button('REMOVE')
            remove.get_style_context().add_class('grey_linktext')
            remove.set_alignment(1, 0)
            remove.connect('clicked', self._remove_from_playlist_handler, e, playlist_name)
            button_grid.attach(remove, 2, 0, 1, 1)

        if e['local_path'] is None:
            stats_str = '{}K views - {}:{} min - by {}'.format(int(e['viewcount'] / 1000.0), e['duration_min'],
                                                               e['duration_sec'], e['author'])
            label = Gtk.Label(stats_str)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            button_grid.attach(label, 1, 1, 2, 1)

            desc_str = e['description'] if len(e['description']) <= 100 else e['description'][:97] + '...'
            label = Gtk.Label(desc_str)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            button_grid.attach(label, 1, 2, 2, 1)

        action_grid = Gtk.Grid()
        button_grid.attach(action_grid, 1, 3, 2, 1)

        button = Gtk.Button('WATCH')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'])
        action_grid.attach(button, 0, 0, 1, 1)

        if not playlist_name:
            action_grid.attach(Spacer(), 1, 0, 1, 1)

            button = Gtk.Button('SAVE')
            button.get_style_context().add_class('orange_linktext')
            self._button_handler_id = button.connect('clicked', self.add_to_playlist_handler, e)
            action_grid.attach(button, 2, 0, 1, 1)

    def _play_handler(self, _button, _url, _localfile):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)

        Gtk.main_iteration_do(True)

        win = self.get_toplevel()

        fullscreen = win.view.play_mode.is_fullscreen()
        play_video(_button, _url, _localfile, fullscreen)

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def add_to_playlist_handler(self, _, video):
        popup = AddToPlaylistPopup(video)
        popup.show_all()

    def _remove_from_playlist_handler(self, _button, video, name):
        confirm = KanoDialog('Are you sure?',
                             'You are about to delete this video from the playlist called "{}"'.format(name),
                             {'OK': True, 'CANCEL': False})
        response = confirm.run()
        if response:
            playlistCollection.collection[name].remove(video)

            win = self.get_toplevel()
            win.switch_view('playlist', name)

    def _detail_view_handler(self, _, video, playlist_name=None):
        win = self.get_toplevel()
        win.switch_view('detail', video=video, playlist=playlist_name)


class VideoDetailEntry(Gtk.Button):
    _ENTRY_HEIGHT = 110
    _TITLE_HEIGHT = 20
    _DESC_HEIGHT = 15
    _INFO_HEIGHT = 15

    def __init__(self, e, playlist_name=None):
        super(VideoDetailEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(30)
        self.add(button_grid)

        if e['big_thumb']:
            img = Gtk.Image()

            big_thumb = '{}/video_large_{}.jpg'.format(tmp_dir, time())
            urlretrieve(e['big_thumb'], big_thumb)
            img.set_from_file(big_thumb)
        else:
            img = Gtk.EventBox()
        img.set_size_request(self._ENTRY_HEIGHT, self._ENTRY_HEIGHT)
        img.get_style_context().add_class('thumb')
        button_grid.attach(img, 0, 0, 1, 1)

        info_grid = Gtk.Grid()
        button_grid.attach(info_grid, 1, 0, 1, 1)

        title_str = e['title']
        label = Gtk.Label(title_str, hexpand=True)
        label.set_line_wrap(True)
        label.set_alignment(0, 0.5)
        label.get_style_context().add_class('title')
        info_grid.attach(label, 1, 0, 1, 1)

        if playlist_name:
            remove = Gtk.Button('REMOVE')
            remove.get_style_context().add_class('grey_linktext')
            remove.set_alignment(1, 0)
            remove.connect('clicked', self._remove_from_playlist_handler, e, playlist_name)
            button_grid.attach(remove, 2, 0, 1, 1)

        if e['local_path'] is None:
            stats_str = '{}K views - {}:{} min - by {}'.format(int(e['viewcount'] / 1000.0), e['duration_min'],
                                                               e['duration_sec'], e['author'])
            label = Gtk.Label(stats_str)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            info_grid.attach(label, 0, 1, 2, 1)

            desc_str = e['description']
            label = Gtk.Label(desc_str)
            label.set_line_wrap(True)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            info_grid.attach(label, 0, 2, 2, 1)

        action_grid = Gtk.Grid()
        info_grid.attach(action_grid, 0, 3, 2, 1)

        button = Gtk.Button('WATCH')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'])
        action_grid.attach(button, 0, 0, 1, 1)

        if not playlist_name:
            action_grid.attach(Spacer(), 1, 0, 1, 1)

            button = Gtk.Button('SAVE')
            button.get_style_context().add_class('orange_linktext')
            self._button_handler_id = button.connect('clicked', self.add_to_playlist_handler, e)
            action_grid.attach(button, 2, 0, 1, 1)

    def _play_handler(self, _button, _url, _localfile):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)

        Gtk.main_iteration_do(True)

        win = self.get_toplevel()

        fullscreen = win.view.play_mode.is_fullscreen()
        play_video(_button, _url, _localfile, fullscreen)

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def add_to_playlist_handler(self, _, video):
        popup = AddToPlaylistPopup(video)
        popup.show_all()

    def _remove_from_playlist_handler(self, _button, video, name):
        confirm = KanoDialog('Are you sure?',
                             'You are about to delete this video from the playlist called "{}"'.format(name),
                             {'OK': True, 'CANCEL': False})
        response = confirm.run()
        if response:
            playlistCollection.collection[name].remove(video)

            win = self.get_toplevel()
            win.switch_view('playlist', name)


class VideoList(Gtk.EventBox):

    def __init__(self, videos=None, playlist=None):
        super(VideoList, self).__init__(hexpand=True)

        self.get_style_context().add_class('video_list')

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(0)

        self.add(self._grid)

        self._no_results = Gtk.Label('No results to display')
        self._no_results.get_style_context().add_class('subtitle')

        if videos is not None:
            i = 0
            for v in videos:
                entry = VideoEntry(v, playlist)
                self._grid.attach(entry, 0, i, 1, 1)
                i += 1


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
                     'local_path': fullpath,
                     'thumbnail': None,
                     'big_thumb': None}

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i + 1, 1, 1)
        else:
            self._grid.attach(self._no_results, 0, 0, 1, 1)


class VideoListYoutube(VideoList):

    def __init__(self, keyword=None, username=None, playlist=None, page=1):
        super(VideoListYoutube, self).__init__()

        self.get_style_context().add_class('video_list_youtube')

        start_index = ((page - 1) * 10) + page
        entries = None

        if keyword:
            entries = search_youtube_by_keyword(keyword, start_index=start_index)
            print 'searching by keyword: ' + keyword
        elif username:
            entries = search_youtube_by_user(username)
            print 'listing by username: ' + username
        elif playlist:
            entries = playlist
            print 'listing playlist: ' + playlist
        else:
            entries = search_youtube_by_user('KanoComputing')
            print 'listing default videos by KanoComputing'

        if entries:
            parsed_entries = parse_youtube_entries(entries)
            for i, e in enumerate(parsed_entries):
                e['local_path'] = None

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i, 1, 1)
        else:
            self._grid.attach(self._no_results, 0, 0, 1, 1)


class VideoListPopular(VideoList):

    def __init__(self):
        super(VideoListPopular, self).__init__()

        self.get_style_context().add_class('video_list_popular')

        entries = search_youtube_by_keyword(popular=True, max_results=3)

        if entries:
            parsed_entries = parse_youtube_entries(entries)
            x_pos = 0

            for i, e in enumerate(parsed_entries):
                img = Gtk.Image()

                button = Gtk.Button()
                if e['big_thumb']:
                    thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())
                    urlretrieve(e['big_thumb'], thumbnail)
                    img.set_from_file(thumbnail)
                button.add(img)
                button.connect('clicked', self._play, e['video_url'])
                self._grid.attach(button, x_pos, 0, 1, 1)

                x_pos += 1

    def _play(self, _button, _url):
        play_video(_button, video_url=_url, fullscreen=True)
