import os
from gi.repository import Gtk
from urllib import urlretrieve
from time import time

from kano.utils import list_dir

from .popups import AddToPlaylistPopup
from .player import play_video, stop_videos
from .youtube import search_youtube_by_user, parse_youtube_entries, \
    search_youtube_by_keyword, tmp_dir

from .general_ui import Spacer


class VideoEntry(Gtk.Button):
    _ENTRY_HEIGHT = 110
    _TITLE_HEIGHT = 20
    _DESC_HEIGHT = 15
    _INFO_HEIGHT = 15

    def __init__(self, e):
        super(VideoEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        # TODO: Add detailed view
        # self.connect('clicked', playlist_cb, name)

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(30)
        self.add(button_grid)

        x_pos = 0

        img = Gtk.Image()

        if e['thumbnail']:
            thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())
            urlretrieve(e['thumbnail'], thumbnail)
            img.set_from_file(thumbnail)
        img.set_size_request(self._ENTRY_HEIGHT, self._ENTRY_HEIGHT)
        img.get_style_context().add_class('thumb')
        button_grid.attach(img, x_pos, 0, 1, 4)
        x_pos += 1

        title_str = e['title'] if len(e['title']) <= 48 else e['title'][:45] + '...'
        label = Gtk.Label(title_str)
        label.set_alignment(0, 0.5)
        label.get_style_context().add_class('title')
        button_grid.attach(label, x_pos, 0, 1, 1)

        if e['local_path'] is None:
            stats_str = '{}K views - {}:{} min - by {}'.format(int(e['viewcount'] / 1000.0), e['duration_min'],
                                                               e['duration_sec'], e['author'])
            label = Gtk.Label(stats_str)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            button_grid.attach(label, x_pos, 1, 1, 1)

            desc_str = e['description'] if len(e['description']) <= 70 else e['description'][:67] + '...'
            label = Gtk.Label(desc_str)
            label.get_style_context().add_class('subtitle')
            label.set_alignment(0, 0.5)
            button_grid.attach(label, x_pos, 2, 1, 1)

        action_grid = Gtk.Grid()
        button_grid.attach(action_grid, x_pos, 3, 1, 1)

        button = Gtk.Button('WATCH')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'], False)
        action_grid.attach(button, 0, 0, 1, 1)

        action_grid.attach(Spacer(), 1, 0, 1, 1)

        button = Gtk.Button('SAVE')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self.add_to_playlist_handler, e)
        action_grid.attach(button, 2, 0, 1, 1)

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

    def add_to_playlist_handler(self, _, video):
        popup = AddToPlaylistPopup(video)
        popup.show_all()


class VideoList(Gtk.EventBox):

    def __init__(self, videos=None):
        super(VideoList, self).__init__(hexpand=True)

        self.get_style_context().add_class('video_list')

        self._grid = Gtk.Grid()
        self._grid.set_row_spacing(10)
        self._grid.set_column_spacing(0)

        self.add(self._grid)

        if videos is not None:
            i = 0
            for v in videos:
                entry = VideoEntry(v)
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
                     'thumbnail': None}

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i + 1, 1, 1)


class VideoListYoutube(VideoList):

    def __init__(self, keyword=None, username=None, playlist=None):
        super(VideoListYoutube, self).__init__()

        self.get_style_context().add_class('video_list_youtube')

        entries = None

        if keyword:
            entries = search_youtube_by_keyword(keyword)
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
