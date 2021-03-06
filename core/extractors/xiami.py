#!/usr/bin/env python  
#-*- coding:utf-8 _*-  
"""
@author: HJK 
@file: xiami.py 
@time: 2019-01-21

从虾米搜索和下载音乐

"""

import datetime
import glovar
from core.common import *
from core.exceptions import *
from utils.customlog import CustomLog

logger = CustomLog(__name__).getLogger()

def xiami_search(keyword) -> list:
    ''' 搜索音乐 '''
    count = glovar.get_option('count') or 5
    params = {
        'key': keyword,
        'v': '2.0',
        'app_key': '1',
        'r': 'search/songs',
        'page': 1,
        'limit': count
    }
    s = requests.Session()
    s.headers.update(glovar.FAKE_HEADERS)
    # 获取cookie
    s.get('http://m.xiami.com')
    s.headers.update({'referer': 'http://m.xiami.com/'})

    music_list = []
    r = s.get('http://api.xiami.com/web', params=params)
    if r.status_code != requests.codes.ok:
        raise RequestError(r.text)
    j = r.json()

    for m in j['data']['songs']:
        # 如果无版权则不显示
        if not m['listen_file']: continue
        music = {
            'title': m['song_name'],
            'id': m['song_id'],
            'singer': m['artist_name'],
            'album': m['album_name'],
            'url': m['listen_file'],
            'source': 'xiami'
        }

        mr = s.get('http://www.xiami.com/song/playlist/id/%s/type/0/cat/json' % m['song_id'])
        if mr.status_code != requests.codes.ok:
            raise RequestError(mr.text)
        mj = mr.json()
        mj_music = mj['data']['trackList'][0]
        music['duration'] = str(datetime.timedelta(seconds=mj_music['length']))
        music['rate'] = 128
        music['ext'] = 'mp3'
        music['name'] = '%s - %s.%s' % (music['singer'], music['title'], music['ext'])

        # 尝试获取虾米高品质音乐(320K)
        url = music['url'].replace('m128.xiami.net', 'm320.xiami.net')
        size = content_length(url)
        if size:
            music['size'] = round(size / 1048576, 2)
            music['url'] = url
            music['rate'] = 320
        else:
            music['size'] = round(content_length(music['url']) / 1048576, 2)

        music_list.append(music)

    return music_list


def xiami_download(music):
    ''' 从虾米音乐下载音乐 '''
    music_download(music)

search = xiami_search
download = xiami_download


