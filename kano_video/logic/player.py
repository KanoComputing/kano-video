#!/usr/bin/env python

# player.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
import os

from kano.utils import is_installed, run_bg, get_volume, percent_to_millibel
from kano.logging import logger
from .youtube import get_video_file_url

# Support for Gtk versions 3 and 2
try:
    from gi.repository import Gtk, Gdk, GObject
except ImportError:
    import gtk as Gtk
    import gtk.gdk as Gdk
    import gobject as GObject

import playudev

subtitles_dir = '/usr/share/kano-media/videos/subtitles'

omxplayer_present = is_installed('omxplayer')
vlc_present = is_installed('vlc')
if not omxplayer_present and not vlc_present:
    sys.exit('Neither vlc nor omxplayer is installed!')


def play_video(_button=None, video_url=None, localfile=None, subtitles=None, init_threads=True):

    if video_url:
        logger.info('Getting video url: {}'.format(video_url))
        success, data = get_video_file_url(video_url)
        if not success:
            logger.error('Error with getting Youtube url: {}'.format(data))
            if _button:
                GObject.idle_add (_button.set_sensitive, True)
            return
        link = data

    elif localfile:
        link = localfile
    else:
        if _button:
            GObject.idle_add (_button.set_sensitive, True)
        return

    logger.info('Launching player...')

    if omxplayer_present:
        HDMI = False
        try:
            from kano_settings.config_file import get_setting
            logger.info('audio:', get_setting('Audio'))
            HDMI = get_setting('Audio') == 'HDMI'
        except Exception:
            pass

        hdmi_str = ''
        if HDMI:
            hdmi_str = '-o hdmi'

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

        subtitles_str = '--subtitle "{subtitles}" ' \
            '--font "/usr/share/fonts/kano/Bariol_Regular.otf" --font-size 35 ' \
            '--align center'.format(subtitles=subtitles)

        player_cmd = 'omxplayer {hdmi_str} {volume_str} {subtitles} -b ' \
                     '"{link}"'.format(link=link, hdmi_str=hdmi_str,
                                       volume_str=volume_str,
                                       subtitles=subtitles_str)
    else:
        player_cmd = 'vlc -f --no-video-title-show ' \
            '"{link}"'.format(link=link)

    # Play with keyboard interaction coming from udev directly
    # so that we do not lose focus and capture all key presses
    playudev.run_player(player_cmd, init_threads)

    # finally, enable the button back again
    if _button:
        GObject.idle_add (_button.set_sensitive, True)


def get_centred_coords(width, height):
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
    if omxplayer_present:
        run_bg('killall omxplayer.bin')
    else:
        run_bg('killall vlc')
