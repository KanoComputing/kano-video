#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

# setting up directories
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# media dir
media_local = os.path.join(dir_path, 'media')
media_usr = '/usr/share/kano-video/media/'

if os.path.exists(media_local):
    media_dir = media_local
elif os.path.exists(media_usr):
    media_dir = media_usr
else:
    raise Exception('Neither local nor usr media dir found!')

image_dir = os.path.join(media_dir, 'images')
css_dir = os.path.join(media_dir, 'CSS')
