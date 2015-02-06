# video.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
#


import threading

from gi.repository import Gtk, Gdk
from time import time
from random import randint

from kano.logging import logger
from kano.gtk3.kano_dialog import KanoDialog
from kano.utils import download_url

from kano_video.paths import image_dir
from kano_video.logic.player import play_video
from kano_video.logic.youtube import search_youtube_by_user, \
    parse_youtube_entries, search_youtube_by_keyword, tmp_dir, \
    page_to_index
from kano_video.logic.playlist import playlistCollection, \
    library_playlist

from .popup import AddToPlaylistPopup
from .general import Spacer, RemoveButton, Button


class VideoEntry(Gtk.Button):
    """
    A widget to display an individual video
    """
    _ENTRY_HEIGHT = 110
    _TITLE_HEIGHT = 20
    _DESC_HEIGHT = 15
    _INFO_HEIGHT = 15

    def __init__(self, e, playlist_name=None, permanent=False):
        super(VideoEntry, self).__init__(hexpand=True)

        self._playlist_name = playlist_name
        self._permanent = permanent

        self.get_style_context().add_class('entry_item')

        self.connect('clicked', self._detail_view_handler, e)

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(30)
        self.add(button_grid)

        img = Gtk.Image()

        if e['thumbnail']:
            thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())
            download_url(e['thumbnail'], thumbnail)
            img.set_from_file(thumbnail)
        else:
            img.set_from_file('{}/icons/no_thumbnail.png'.format(image_dir))

        img.set_size_request(self._ENTRY_HEIGHT, self._ENTRY_HEIGHT)
        img.get_style_context().add_class('thumb')
        button_grid.attach(img, 0, 0, 1, 4)

        title_str = e['title'] if len(e['title']) <= 70 else e['title'][:67] + '...'
        label = Gtk.Label(title_str, hexpand=True)
        label.set_alignment(0, 0.5)
        label.get_style_context().add_class('title')
        button_grid.attach(label, 1, 0, 1, 1)

        if playlist_name and not permanent:
            remove = RemoveButton()
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

        button = Button('WATCH')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'])
        action_grid.attach(button, 0, 0, 1, 1)

        if not playlist_name:
            action_grid.attach(Spacer(), 1, 0, 1, 1)

            button = Button('SAVE')
            button.get_style_context().add_class('orange_linktext')
            self._button_handler_id = button.connect('clicked', self.add_to_playlist_handler, e)
            action_grid.attach(button, 2, 0, 1, 1)

    def _play_handler(self, _button, _url, _localfile):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)

        # disable the button so it is not triggered while the video is playing
        _button.set_sensitive(False)

        # start the video playing thread - this will enable the button back again
        t = threading.Thread(target=play_video, args=(_button, _url, _localfile, None, False))
        t.daemon = True
        t.start()

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def add_to_playlist_handler(self, _, video):
        popup = AddToPlaylistPopup(video, self.get_toplevel())
        popup.run()

    def _remove_from_playlist_handler(self, _button, video, name):
        confirm = KanoDialog('Are you sure?',
                             'You are about to delete this video from the playlist called "{}"'.format(name),
                             {'OK': {'return_value': True}, 'CANCEL': {'return_value': False}},
                             parent_window=self.get_toplevel())
        response = confirm.run()
        if response:
            playlistCollection.collection[name].remove(video)

            win = self.get_toplevel()
            win.switch_view('playlist', name)

    def _detail_view_handler(self, _, video):
        win = self.get_toplevel()
        win.switch_view('detail', video=video,
                        playlist=self._playlist_name,
                        permanent=self._permanent)


class VideoDetailEntry(Gtk.Button):
    """
    A widget that displays detailed information about a video
    """
    _ENTRY_HEIGHT = 110
    _TITLE_HEIGHT = 20
    _DESC_HEIGHT = 15
    _INFO_HEIGHT = 15

    def __init__(self, e, playlist_name=None, permanent=False):
        super(VideoDetailEntry, self).__init__(hexpand=True)

        self.get_style_context().add_class('entry_item')

        button_grid = Gtk.Grid()
        button_grid.set_column_spacing(30)
        self.add(button_grid)

        img = Gtk.Image()

        if e['big_thumb']:
            big_thumb = '{}/video_large_{}.jpg'.format(tmp_dir, time())
            download_url(e['big_thumb'], big_thumb)
            img.set_from_file(big_thumb)
        else:
            img.set_from_file('{}/icons/no_thumbnail.png'.format(image_dir))

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

        if playlist_name and not permanent:
            remove = RemoveButton()
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

        button = Button('WATCH')
        button.get_style_context().add_class('orange_linktext')
        self._button_handler_id = button.connect('clicked', self._play_handler, e['video_url'], e['local_path'])
        action_grid.attach(button, 0, 0, 1, 1)

        if not playlist_name:
            action_grid.attach(Spacer(), 1, 0, 1, 1)

            button = Button('SAVE')
            button.get_style_context().add_class('orange_linktext')
            self._button_handler_id = button.connect('clicked', self.add_to_playlist_handler, e)
            action_grid.attach(button, 2, 0, 1, 1)

    def _play_handler(self, _button, _url, _localfile):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)

        # disable the button so it is not triggered while the video is playing
        _button.set_sensitive(False)

        # start the video playing thread - this will enable the button back again
        t = threading.Thread(target=play_video, args=(_button, _url, _localfile, None, False))
        t.daemon = True
        t.start()

        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_root_window().set_cursor(cursor)

    def add_to_playlist_handler(self, _, video):
        popup = AddToPlaylistPopup(video, self.get_toplevel())
        popup.show_all()

    def _remove_from_playlist_handler(self, _button, video, name):
        confirm = KanoDialog('Are you sure?',
                             'You are about to delete this video from the playlist called "{}"'.format(name),
                             {'OK': {'return_value': True}, 'CANCEL': {'return_value': False}},
                             parent_window=self.get_toplevel())
        response = confirm.run()
        if response:
            playlistCollection.collection[name].remove(video)

            win = self.get_toplevel()
            win.switch_view('playlist', name)


class VideoList(Gtk.EventBox):
    """
    A list of a collection of videos
    """

    def __init__(self, videos=None, playlist=None, permanent=False):
        super(VideoList, self).__init__(hexpand=True)

        # Try to get parental boolean flag from kano-settings
        # By default we assume parental control is turned OFF
        self.ParentalControl = False
        try:
            from kano_settings.set_advance.parental import get_parental_enabled
            if get_parental_enabled():
                self.ParentalControl = True
        except Exception:
            pass

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
                entry = VideoEntry(v, playlist_name=playlist, permanent=permanent)
                self._grid.attach(entry, 0, i, 1, 1)
                i += 1


class VideoListLocal(VideoList):
    """
    A video collection list used for locally stored videos
    """

    def __init__(self, open_folder_dialog=False):
        super(VideoListLocal, self).__init__()

        self.get_style_context().add_class('video_list_local')

        if library_playlist.playlist:
            for i, e in enumerate(library_playlist.playlist):
                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i + 1, 1, 1)
        else:
            self._grid.attach(self._no_results, 0, 0, 1, 1)


class VideoListYoutube(VideoList):
    """
    A video collection list used for videos on Youtube
    """

    def __init__(self, keyword=None, username=None, playlist=None, page=1):
        super(VideoListYoutube, self).__init__()

        self.get_style_context().add_class('video_list_youtube')

        start_index = page_to_index(page)
        entries = None
        self._parsed_entries = None

        if keyword:
            entries = search_youtube_by_keyword(
                keyword, start_index=start_index,
                parent_control=self.ParentalControl)
            logger.info('searching by keyword: ' + keyword)
        elif username:
            entries = search_youtube_by_user(
                username, parent_control=self.ParentalControl)
            logger.info('listing by username: ' + username)
        elif playlist:
            entries = playlist
            logger.info('listing playlist: ' + playlist)
        else:
            entries = search_youtube_by_user(
                'KanoComputing', parent_control=self.ParentalControl)
            logger.info('listing default videos by KanoComputing')

        if entries:
            self._parsed_entries = parse_youtube_entries(entries)
        else:
            self._grid.attach(self._no_results, 0, 0, 1, 1)

        self.refresh()

    def refresh(self):
        if self._parsed_entries:
            for i, e in enumerate(self._parsed_entries):
                e['local_path'] = None

                entry = VideoEntry(e)
                self._grid.attach(entry, 0, i, 1, 1)


class VideoListPopular(VideoList):
    """
    A selection of videos that are popular on Youtube
    """

    def __init__(self):
        super(VideoListPopular, self).__init__()

        self.get_style_context().add_class('video_list_popular')

        entries = search_youtube_by_keyword(popular=True, max_results=3,
                                            parent_control=self.ParentalControl,
                                            start_index=randint(1, 20))

        if entries:
            parsed_entries = parse_youtube_entries(entries)
            x_pos = 0

            for i, e in enumerate(parsed_entries):
                img = Gtk.Image()

                button = Button()
                if e['big_thumb']:
                    thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())
                    download_url(e['big_thumb'], thumbnail)
                    img.set_from_file(thumbnail)
                button.add(img)
                button.connect('clicked', self._play, e['video_url'])
                self._grid.attach(button, x_pos, 0, 1, 1)

                x_pos += 1

    def _play(self, _button, _url):
        # disable the button so it is not triggered while the video is playing
        _button.set_sensitive(False)

        # start the video playing thread - this will enable the button back again
        t = threading.Thread(target=play_video, args=(_button, _url, None, False))
        t.daemon = True
        t.start()
