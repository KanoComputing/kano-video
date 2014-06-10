#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
from gi.repository import Gdk

from kano.utils import write_file_contents, is_installed, run_bg, is_running, run_cmd
from kano.logging import logger
from .youtube import get_video_file_url

omxplayer_present = is_installed('omxplayer')
vlc_present = is_installed('vlc')
if not omxplayer_present and not vlc_present:
    sys.exit('Neither vlc nor omxplayer is installed!')


def play_video(_button=None, video_url=None, localfile=None, fullscreen=False, wait=False):
    if video_url:
        logger.info('Getting video url: {}'.format(video_url))
        success, data = get_video_file_url(video_url)
        if not success:
            logger.error('Error with getting Youtube url: {}'.format(data))
            return
        link = data

    if localfile:
        link = localfile

    logger.info('Launching player...')

    width = 480
    height = 270

    if omxplayer_present:
        x1, y1, x2, y2 = get_centred_coords(width=width, height=height)
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

        if fullscreen:
            player_cmd = 'lxterminal -e "omxplayer {hdmi_str} -b \\"{link}\\""'.format(link=link, hdmi_str=hdmi_str)
        else:
            file_str = 'kano-window-tool -dno -t ' \
                'omxplayer -x {x} -y {y} -w {width} -h {height}\n'.format(x=x1, y=y1, width=width, height=height)
            file_str += 'omxplayer {hdmi_str} ' \
                '--win "{x1} {y1} {x2} {y2}" ' \
                '"{link}"\n'.format(link=link, hdmi_str=hdmi_str, x1=x1, y1=y1, x2=x2, y2=y2)
            file_path = '/tmp/omxplayer.sh'
            write_file_contents(file_path, file_str)
            player_cmd = 'lxterminal -t omxplayer -e "bash {}"'.format(file_path)
    else:
        if fullscreen:
            player_cmd = 'vlc -f --no-video-title-show "{link}"'.format(link=link)
        else:
            player_cmd = 'vlc --width {width} --no-video-title-show "{link}"'.format(link=link, width=width)

    if not fullscreen and is_running('kdesk'):
        player_cmd = '/usr/bin/kdesk-blur \'{}\''.format(player_cmd)

    if wait:
        run_cmd(player_cmd)
    else:
        run_bg(player_cmd)


def get_centred_coords(width, height):
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
