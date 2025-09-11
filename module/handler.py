# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:33
# File:handler.py
import time
import sched
import datetime
from typing import Callable

from module import log, console


class Handler:
    @staticmethod
    def __to_hour_minute(seconds):
        remain_seconds = seconds % (24 * 3600)
        remain_hours = remain_seconds // 3600
        remain_seconds %= 3600
        remain_minutes = remain_seconds // 60
        return remain_hours, remain_minutes, remain_seconds

    @staticmethod
    def task(func: Callable, **kwargs):
        schedule_tables = [
            '00:00'
        ]
        today = datetime.datetime.now().date()
        remain_do_time = []
        scheduler = sched.scheduler(time.time, time.sleep)
        for time_str in schedule_tables:
            scheduled_time = datetime.datetime.strptime(f'{today} {time_str}', '%Y-%m-%d %H:%M')
            if scheduled_time < datetime.datetime.now():
                scheduled_time += datetime.timedelta(days=1)
            delay = (scheduled_time - datetime.datetime.now()).total_seconds()
            remain_do_time.append(delay)
        next_do_time = min(remain_do_time)
        scheduler.enter(next_do_time, 1, func, kwargs=kwargs)
        p1 = f'开始执行任务,当前时间:{datetime.datetime.now()}'
        p2 = f'距离下次执行任务还有%d:%02d:%02d' % (Handler.__to_hour_minute(next_do_time))
        log.info(p1)
        log.info(p2)
        console.log(p1)
        console.log(p2)
        scheduler.run()
