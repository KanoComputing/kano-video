#!/usr/bin/python

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


def wait_for_keys(pomx):
    '''
    Listens for keyboard events from /dev/input
    translates ESC, Q, Space, P, -, + to omxplayer via its stdin.
    pomx is a subprocess Popen object.
    '''

    # FIXME: Eventually event0 is eventX on some keyboards
    infile_path = "/dev/input/event0"

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

        if (type == 1 and code == 1 and value == 0) or (type == 1 and code == 16 and value == 0):
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

        event = in_file.read(EVENT_SIZE)

    in_file.close()


def run_player(cmdline):
    '''
    Start omxplayer giving us the stdin pipe to speak to him.
    '''
    pomx = subprocess.Popen(cmdline, stdin=subprocess.PIPE, shell=True)

    # A thread will listen for key events and send them to OMXPlayer
    t = threading.Thread(target=wait_for_keys, args=(pomx,))
    t.daemon = True
    t.start()

    rc = pomx.wait()
    return rc
