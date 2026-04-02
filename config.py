# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:19
# File:config.py
import random

activity_id: str = '885966'
flow_id: str = '1197212'
sd_id: str = ''.join(random.choices('0123456789abcdef', k=32))
special_date: list = ['2026-04-01', '2026-04-10', '2026-04-17', '2026-04-24']
special_date_flow_id: str = '1197216'
cumulative_day: list = [3, 5, 9, 15, 20, 25]
cumulative_day_flow_id: str = '1197211'
