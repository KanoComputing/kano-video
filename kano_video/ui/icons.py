#!/usr/bin/env python

# icons.py
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Creates pixbufs that we can use to make images from.
# Uses a strip of icons, each 24px by 24px.
#

from gi.repository import Gtk, GdkPixbuf
from kano_video.paths import image_dir

# To make an image using the pixbuf icon, use the command below:
# image.set_from_pixbuf(self.pixbuf)


def set_from_name(name):
    """
    Get a Gtk Image widget from the name of the image
    """

    icons = {
        "badge": 0,
        "challenge": 1,
        "swag": 2,
        "next_arrow": 3,
        "prev_arrow": 4,
        "locked": 5,
        "cross": 6,
        "unlocked": 7
    }

    icon_number = icons[name] if name in icons else 0

    # Create main window
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
        image_dir + '/icons/systemsetup-icons.png', 192, 24
    )
    subpixbuf = (
        pixbuf
        .new_subpixbuf(24 * icon_number, 0, 24, 24)
        .add_alpha(True, 255, 255, 255)
    )

    image = Gtk.Image()
    image.set_from_pixbuf(subpixbuf)

    return image
