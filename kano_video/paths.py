#!/usr/bin/env python

# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Handles resolving directory paths for platform-independent use

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
usr_path = '/usr/share/kano-video'


def get_dir_path(dir):
    """
    Gets the actual path for a relative directory.
    Distinguishes between installs and development environments.
    """

    local = os.path.join(dir_path, dir)
    usr = os.path.join(usr_path, dir)

    if os.path.exists(local):
        return local
    elif os.path.exists(usr):
        return usr
    else:
        raise Exception('Neither local nor usr {dir} dir found!'.format(dir=dir))

playlist_path = get_dir_path('playlists')
media_dir = get_dir_path('media')
image_dir = os.path.join(media_dir, 'images')
css_dir = os.path.join(media_dir, 'CSS')
icon_dir = get_dir_path('icon')
