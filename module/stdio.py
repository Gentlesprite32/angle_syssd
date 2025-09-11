# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/11 16:14
# File:stdio.py
import os

from module import log


def get_cookie():
    return __get_info('cookies.txt', '没有找到cookie,尝试从环境变量中获取...')


def get_push_key():
    return __get_info('push_key.txt', '没有找到push_key,如果没有配置环境变量,领取信息将不会进行推送。')


def __get_info(file, message):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            f.write('')
        log.warning(message)
        return None

    with open(file, 'r', encoding='utf-8') as f:
        cookie_content = f.read().strip()

    if cookie_content:
        if cookie_content.startswith("'"):
            cookie_content = cookie_content[1:]  # 去掉开头的'
        if cookie_content.endswith("'"):
            cookie_content = cookie_content[:-1]  # 去掉结尾的'
        return cookie_content
    else:
        log.warning(message)
        return None
