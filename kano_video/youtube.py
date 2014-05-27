#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
import os
from urllib import urlretrieve
from shutil import rmtree
from time import time
from kano.utils import requests_get_json, run_cmd


def search_youtube_by_keyword(keyword=None, popular=False):
    url = 'http://gdata.youtube.com/feeds/api/videos'
    params = {
        'vq': keyword,
        'racy': 'exclude',
        'orderby': 'relevance',
        'alt': 'json',
        'max-results': 10
    }
    if popular:
        params['orderby'] = 'viewCount'
    success, error, data = requests_get_json(url, params=params)
    if not success:
        sys.exit(error)
    if 'feed' in data and 'entry' in data['feed']:
        return data['feed']['entry']


def search_youtube_by_user(username):
    url = 'http://gdata.youtube.com/feeds/users/{}/uploads'.format(username)
    params = {
        'alt': 'json',
        'orderby': 'viewCount',
        'max-results': 10
    }
    success, error, data = requests_get_json(url, params=params)
    if not success:
        sys.exit(error)
    if 'feed' in data and 'entry' in data['feed']:
        return data['feed']['entry']


def parse_youtube_entries(entries):
    tmp_dir = '/tmp/kano-video'
    if os.path.exists(tmp_dir):
        rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    my_entries = list()
    for e in entries:
        for thumb in e['media$group']['media$thumbnail']:
            if thumb['width'] is 120 and thumb['height'] is 90:
                thumbnail = '{}/video_{}.jpg'.format(tmp_dir, time())

                urlretrieve(thumb['url'], thumbnail)
                break

        author = e['author'][0]['name']['$t']
        title = e['title']['$t']
        description = e['media$group']['media$description']['$t']
        video_url = e['media$group']['media$player'][0]['url']
        duration = int(e['media$group']['yt$duration']['seconds'])
        duration_min = duration / 60
        duration_sec = duration % 60
        viewcount = int(e['yt$statistics']['viewCount'])
        entry_data = {
            'author': author,
            'title': title,
            'description': description,
            'video_url': video_url,
            'duration': duration,
            'duration_min': duration_min,
            'duration_sec': duration_sec,
            'viewcount': viewcount,
            'thumbnail': thumbnail
        }
        my_entries.append(entry_data)
    return my_entries


def get_video_file_url(video_url):
    cmd = 'youtube-dl -g {}'.format(video_url)
    o, e, _ = run_cmd(cmd)
    if e:
        return False, e
    return True, o.strip()
