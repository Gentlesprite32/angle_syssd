# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:19
# File:config.py
import random

activity_id: str = '880706'
flow_id: str = '1192657'
sd_id: str = ''.join(random.choices('0123456789abcdef', k=32))
special_date: list = ['2026-03-03', '2026-03-13', '2026-03-20', '2026-03-27']
special_date_flow_id: str = '1192661'
cumulative_day: list = [3, 5, 9, 15, 20, 25]
cumulative_day_flow_id: str = '1192656'
