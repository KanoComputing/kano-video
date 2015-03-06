#!/usr/bin/env python

# player.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Manages playing of videos
#

import sys
import os

from kano.utils import is_installed, run_bg, get_volume, percent_to_millibel
from kano.logging import logger
from .youtube import get_video_file_url


# Support for Gtk versions 3 and 2
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import playudev

subtitles_dir = '/usr/share/kano-media/videos/subtitles'

omxplayer_present = is_installed('omxplayer')
vlc_present = is_installed('vlc')
if not omxplayer_present and not vlc_present:
    sys.exit('Neither vlc nor omxplayer is installed!')


def play_video(_button=None, video_url=None, localfile=None, subtitles=None, \
                   init_threads=True, keyboard_engulfer=True):
    """
    Plays a local or remote video using the optimal video player found.
    Handles sound settings and subtitles.
    """

    if video_url:
        logger.info('Getting video url: {}'.format(video_url))
        success, data = get_video_file_url(video_url)
        if not success:
            logger.error('Error with getting Youtube url: {}'.format(data))
            if _button:
                _button.set_sensitive(True)
            return
        link = data

    elif localfile:
        link = localfile
    else:
        if _button:
            _button.set_sensitive(True)
        return

    logger.info('Launching player...')

    if omxplayer_present:

        volume_percent, _ = get_volume()
        volume_str = '--vol {}'.format(
            percent_to_millibel(volume_percent, raspberry_mod=True))

        if not subtitles or not os.path.isfile(subtitles):
            subtitles = None

            if localfile:
                filename = os.path.basename(localfile)
                filename = os.path.splitext(filename)[0]
                fullpath = os.path.join(subtitles_dir, filename + '.srt')
                if os.path.exists(fullpath):
                    subtitles = fullpath

            if not subtitles:
                subtitles = os.path.join(subtitles_dir, 'controls.srt')

        subtitles_str = ''
        try:
            from kano_settings.system.display import is_overscan
            if not is_overscan():
                subtitles_str = '--subtitle "{subtitles}" ' \
                    '--font "/usr/share/fonts/kano/Bariol_Regular.otf" --font-size 35 ' \
                    '--align center'.format(subtitles=subtitles)
        except Exception:
            pass

        player_cmd = 'omxplayer -o both {volume_str} {subtitles} -b ' \
                     '"{link}"'.format(link=link, volume_str=volume_str,
                                       subtitles=subtitles_str)
    else:
        player_cmd = 'vlc -f --no-video-title-show ' \
            '"{link}"'.format(link=link)

    # Play with keyboard interaction coming from udev directly
    # so that we do not lose focus and capture all key presses
    playudev.run_player(player_cmd, init_threads=init_threads, \
                            keyboard_engulfer=keyboard_engulfer)

    # finally, enable the button back again
    if _button:
        _button.set_sensitive(True)


def get_centred_coords(width, height):
    """
    Calculates the top-left and bottom-right coordinates for a given window
    size to be centred
    """

    from gi.repository import Gdk

    taskbar_height = 44

    monitor = {
        'width': Gdk.Screen.width(),
        'height': Gdk.Screen.height(),
    }

    x1 = (monitor['width'] - width) / 2
    x2 = x1 + width
    y1 = ((monitor['height'] - taskbar_height) - height) / 2
    y2 = y1 + height

    return x1, y1, x2, y2


def stop_videos(_button=None):
    """
    Kills all videos that are currently playing
    # TODO: Stop only videos which are managed by this module
    """

    if omxplayer_present:
        run_bg('killall omxplayer.bin')
    else:
        run_bg('killall vlc')
