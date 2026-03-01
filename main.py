# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/6 22:16
# File:main.py
import os
import sys

from dotenv import load_dotenv

from module import console
from module.signer import NZSigner
from config import (
    activity_id,
    flow_id,
    sd_id,
    special_date,
    special_date_flow_id,
    cumulative_day,
    cumulative_day_flow_id
)

if __name__ == '__main__':
    load_dotenv()
    cookies = os.getenv('COOKIES')
    push_key = os.getenv('PUSH_KEY')
    if not cookies:
        console.log('没有找到COOKIES,请配置环境变量。')
        sys.exit(1)
    if not push_key:
        console.log('没有找到PUSH_KEY,领取信息不会进行推送。')
    try:
        signer = NZSigner(
            cookies=cookies,
            push_key=push_key,
            activity_id=activity_id,
            flow_id=flow_id,
            sd_id=sd_id,
            special_date=special_date,
            special_date_flow_id=special_date_flow_id,
            cumulative_day=cumulative_day,
            cumulative_day_flow_id=cumulative_day_flow_id
        )
        signer.sign()
    except KeyboardInterrupt:
        console.log('键盘中断。')
