# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:33
# File:notify.py
import urllib.parse
import urllib.request

from module import log


def sc_send(text, desp='', key='[SENDKEY]'):
    try:
        post_data = urllib.parse.urlencode({'text': text, 'desp': desp}).encode('utf-8')
        url = f'https://sctapi.ftqq.com/{key}.send'
        req = urllib.request.Request(url, data=post_data, method='POST')
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
        return result
    except Exception as e:
        log.error(f'推送失败!请检查key:{key}是否有效!原因:"{e}"')
