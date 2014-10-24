#!/usr/bin/env python

# playudev.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Play media using omxplayer, but listening for keyboard events from udev directly
#

import struct
import subprocess
import threading
import csv

from kano.logging import logger

#
# We need to play well with Gtk version 2 and version 3 clients
#
try:
    from gi.repository import Gtk, Gdk, GObject
except ImportError:
    import gtk as Gtk
    import gtk.gdk as Gdk
    import gobject as GObject


def get_keyboard_input_device(fdevice_list='/proc/bus/input/devices'):
    '''
    Most keyboards send data to /dev/input/event0, but some use a different device.
    This function heuristically finds the correct device name that the kernel decides to map.
    We are reading /proc/bus/input/devices in search for an entry H: (handler)
    that says "kbd" alone. The field following that *should* be the device name mapped to keyboard keys.
    Any other combination seems to point to other devices (trackpads and various other goodies)

    "H: Handlers=kbd event0"

    https://www.kernel.org/doc/Documentation/input/input.txt
    '''

    # If we can't find the device, we default to most commonly used
    keyboard_input_device = '/dev/input/event0'

    with open(fdevice_list, 'r') as csvfile:
        input_devices = csv.reader(csvfile, delimiter=' ', lineterminator='\n', skipinitialspace=True)
        for ndevice, device_info in enumerate(input_devices):
            if len(device_info) > 2 and \
               device_info[0] == 'H:' and \
               device_info[1] == 'Handlers=kbd' and \
               len(device_info[2]) and device_info[2].startswith('event'):

                keyboard_input_device = '/dev/input/%s' % device_info[2]
                logger.info('keyboard input device discovered is %s' % keyboard_input_device)
                break

    return keyboard_input_device


def wait_for_keys(pomx):
    '''
    Listens for keyboard events from /dev/input
    translates ESC, Q, Space, P, -, + to omxplayer via its stdin.
    pomx is a subprocess Popen object.
    '''

    # Ask the kernel which device is mapping the input keyboard
    infile_path = get_keyboard_input_device()
    logger.info('wait_for_keys is using keyboard input device: %s' % infile_path)

    #long int, long int, unsigned short, unsigned short, unsigned int
    FORMAT = 'llHHI'
    EVENT_SIZE = struct.calcsize(FORMAT)

    #open file in binary mode
    in_file = open(infile_path, "rb")

    event = in_file.read(EVENT_SIZE)

    while event:
        (tv_sec, tv_usec, type, code, value) = struct.unpack(FORMAT, event)

        # other keys you wish to send to omxplayer should be added here
        # future updates to omxplayer need to be taken into account here

        #print "type {} | code {} | value {}".format(type, code, value)

        try:
            if (type == 1 and code == 1 and value == 0) or (type == 1 and code == 16 and value == 0):

                logger.info('keyboard Esc/Q has been detected, terminating omxplayer')

                # The key "esc" or "q" has been released, quit omxplayer
                pomx.stdin.write('q')
                pomx.stdin.flush()
                
                # finish the thread
                break

            elif (type == 1 and code == 25 and value == 0) or (type == 1 and code == 57 and value == 0):
                # The key "p" or "space" has been released, pause/resume the media
                pomx.stdin.write(' ')
                pomx.stdin.flush()

            elif type == 1 and code == 12 and value == 0:
                # The key "-" has been released, decrease the volume
                pomx.stdin.write('-')
                pomx.stdin.flush()

            elif type == 1 and code == 13 and value == 0:
                # The key "+" has been released, increase the volume
                pomx.stdin.write('+')
                pomx.stdin.flush()

        except IOError:
            # OMXplayer terminated and the pipe is not valid anymore. Terminate this thread
            in_file.close()
            return

        except:
            # We want to attend the user as much as we can, so blindfold on any unrelated problem
            pass

        # read the next event from the keyboard input stream
        event = in_file.read(EVENT_SIZE)

    in_file.close()


def run_video(win, cmdline):
    '''
    Start omxplayer along with a thread to watch the keyboard
    '''
    logger.info('playudev starting video Popen object along with Keyboard event thread')
    pomx = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    # A thread will listen for key events and send them to OMXPlayer
    t = threading.Thread(target=wait_for_keys, args=(pomx,))
    t.daemon = True
    t.start()

    win.rc = pomx.wait()
    logger.info('playudev omxplayer process has terminated')

    win.destroy()


class VideoKeyboardEngulfer(Gtk.Window):
    '''
    Show a fullscreen video to capture all keyboard / Mouse events
    Omxplayer will position itself on top of it.
    '''
    def __init__(self, cmdline):
        Gtk.Window.__init__(self)
        self.fullscreen()
        self.play_video(cmdline)

    def play_video(self, cmdline):
        '''
        Detach a thread to launch omxplayer and a keyboard event watcher
        '''
        t = threading.Thread(target=run_video, args=(self, cmdline,))
        t.daemon = True
        t.start()


def run_player(cmdline, init_threads=True):
    '''
    A popup window in full screen mode will engulf all key and mouse events
    so that underlying windows do not get unintentional input.
    '''
    if init_threads:
        GObject.threads_init()

    win = VideoKeyboardEngulfer(cmdline)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return win.rc
