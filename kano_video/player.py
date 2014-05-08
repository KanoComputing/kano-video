#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os
import sys

from kano.utils import write_file_contents, is_installed
from .youtube import get_video_file_url

omxplayer_present = is_installed('omxplayer')
vlc_present = is_installed('vlc')
if not omxplayer_present and not vlc_present:
    sys.exit('Neither vlc nor omxplayer is installed!')


def play_video(_button, video_url=None, localfile=None, fullscreen=False):
    if video_url:
        print 'Getting video url: {}'.format(video_url)
        success, data = get_video_file_url(video_url)
        if not success:
            print 'Error with getting Youtube url: {}'.format(data)
            return
        link = data

    if localfile:
        link = localfile

    print 'Launching player...'

    if omxplayer_present:
        HDMI = False
        try:
            from kano.profile.apps import load_app_state_variable
            HDMI = load_app_state_variable('kano-settings', 'Audio') == 'HDMI'
        except Exception:
            pass

        hdmi_str = ''
        if HDMI:
            hdmi_str = '-o hdmi'

        if fullscreen:
            player_cmd = 'lxterminal -e "omxplayer {hdmi_str} -b \\"{link}\\""'.format(link=link, hdmi_str=hdmi_str)
        else:
            file_str = 'kano-window-tool -dno -t omxplayer -x 100 -y 100 -w 300 -h 180\n'
            file_str += 'omxplayer {hdmi_str} --win "100 100 420 280" "{link}"\n'.format(link=link, hdmi_str=hdmi_str)
            file_path = '/tmp/omxplayer.sh'
            write_file_contents(file_path, file_str)
            player_cmd = 'lxterminal -t omxplayer -e "bash {}"'.format(file_path)
    else:
        if fullscreen:
            player_cmd = 'vlc -f --no-video-title-show "{link}"'.format(link=link)
        else:
            player_cmd = 'vlc --width 700 --no-video-title-show "{link}"'.format(link=link)

    print player_cmd
    os.system(player_cmd)


def stop_videos(_button):
    if omxplayer_present:
        os.system('killall omxplayer.bin')
    else:
        os.system('killall vlc')
