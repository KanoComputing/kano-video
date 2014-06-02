#!/usr/bin/env python

# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
import os
from shutil import rmtree
from kano.utils import requests_get_json, run_cmd

tmp_dir = '/tmp/kano-video'


def page_to_index(page, max_results=10):
    return ((page - 1) * max_results) + 1


def search_youtube_by_keyword(keyword=None, popular=False, max_results=10, start_index=1):
    url = 'http://gdata.youtube.com/feeds/api/videos'
    params = {
        'vq': keyword,
        'racy': 'exclude',
        'orderby': 'relevance',
        'alt': 'json',
        'max-results': max_results,
        'start-index': start_index
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
    if os.path.exists(tmp_dir):
        rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    my_entries = list()
    for e in entries:
        # Small thumbnail
        for thumb in e['media$group']['media$thumbnail']:
            if thumb['width'] == 120 and thumb['height'] == 90:
                thumbnail = thumb['url']
                break

        # Big thumbnail
        for thumb in e['media$group']['media$thumbnail']:
            if thumb['width'] == 480 and thumb['height'] == 360:
                bigthumb = thumb['url']
                break

        author = e['author'][0]['name']['$t'].encode('utf-8')
        title = e['title']['$t'].encode('utf-8')
        description = e['media$group']['media$description']['$t'].encode('utf-8')
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
            'thumbnail': thumbnail,
            'big_thumb': bigthumb
        }
        my_entries.append(entry_data)
    return my_entries


def get_video_file_url(video_url):
    cmd = 'youtube-dl -g {}'.format(video_url)
    o, e, _ = run_cmd(cmd)
    if e:
        return False, e
    return True, o.strip()
