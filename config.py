# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:19
# File:config.py
import random
from typing import Optional

activity_id: str = '1001016'  # 签到活动ID。
flow_id: str = '1240458'  # 签到礼包。
sd_id: str = ''.join(random.choices('0123456789abcdef', k=32))
special_date: list = ['2026-08-07', '2026-08-14', '2026-08-21', '2026-08-28']
special_date_flow_id: str = str(int(flow_id) + 5)  # 限定日期礼包。
cumulative_day: list = [3, 5, 9, 15, 20, 25]
cumulative_day_flow_id: str = str(int(flow_id) - 1)  # 累计签到礼包。

# 版本福利配置（可选）。
version_gift_activity_id: Optional[str] = '999447'  # 版本福利活动ID。
version_gift_play_flow_id: Optional[str] = '1239768'  # 游玩一局礼包。
version_gift_share_flow_id: str = str(
    int(version_gift_play_flow_id) + 1) if version_gift_play_flow_id else None  # 分享礼包。
version_gift_flow_id: str = str(int(version_gift_play_flow_id) + 2) if version_gift_play_flow_id else None  # 抽奖。
