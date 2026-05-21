# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:19
# File:config.py
import random
from typing import Optional

activity_id: str = '920173'
flow_id: str = '1206535'
sd_id: str = ''.join(random.choices('0123456789abcdef', k=32))
special_date: list = ['2026-05-08', '2026-05-15', '2026-05-22', '2026-05-30']
special_date_flow_id: str = '1206539'
cumulative_day: list = [3, 5, 9, 15, 20, 25]
cumulative_day_flow_id: str = '1206534'

# 版本福利配置（可选）。
version_gift_activity_id: Optional[str] = '924173'
version_gift_play_flow_id: Optional[str] = '1209929'
version_gift_share_flow_id: Optional[str] = '1209930'
version_gift_flow_id: Optional[str] = '1209931'
