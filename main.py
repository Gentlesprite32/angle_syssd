# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/6 22:16
# File:main_refresh.py
# coding=UTF-8
import os
import sys

from module import console
from module.stdio import get_cookie, get_push_key
from module.signer import NZSigner
from module.handler import Handler
from config import activity_id, flow_id, sd_id

if __name__ == '__main__':
    cookies = get_cookie()
    push_key = get_push_key()
    actions_flags = False
    if not cookies:
        cookies = os.getenv('COOKIES')
        push_key = os.getenv('PUSH_KEY')
        if not cookies:
            actions_flags = True
            console.print(
                '请配置以下环境变量或新建config.py设置以下变量后运行。\n'
                '# Linux/macOS 设置教程:export 变量="your_cookie_value_here"\n'
                '# Windows 设置教程:set 变量=your_cookie_value_here\n'
                '需设置以下变量:\n'
                'COOKIES\n'
                'PUSH_KEY(可选)\n'
            )
            sys.exit()
    try:
        signer = NZSigner(cookies=cookies, push_key=push_key)
        signer.sign(
            activity_id=activity_id,
            flow_id=flow_id,
            sd_id=sd_id
        )
        if not actions_flags:
            sys.exit()
        handler = Handler()
        handler.task(
            func=signer.sign,
            activity_id=activity_id,
            flow_id=flow_id,
            sd_id=sd_id,
            handler=handler.task
        )
    except KeyboardInterrupt:
        console.log('键盘中断。')
