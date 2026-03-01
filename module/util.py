# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/11 16:14
# File:util.py
import time
import schedule
from datetime import datetime
from functools import wraps
from typing import Callable, Union, Optional, Hashable

import urllib.parse
import urllib.request

from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from . import log, console
from .parser import PARSE_ARGS


def safe_index(
        obj: Union[list, None],
        value: Hashable,
        start: Optional[int] = 0
) -> Union[int, None]:
    try:
        return obj.index(value) + start
    except (ValueError, AttributeError):
        return None


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


def schedule_task(time_str: Union[str, list] = '00:00:00'):
    def decorator(func: Callable):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)

            if not PARSE_ARGS.loop:
                return result

            time_list = [time_str] if isinstance(time_str, str) else time_str

            for t in time_list:
                schedule.every().day.at(t).do(func, *args, **kwargs)
            time_str_display = '、'.join(time_list)
            p = f'当前时间:{datetime.now()},任务将在每天{time_str_display}执行。'
            log.info(p)
            console.log(p)

            with Live(refresh_per_second=1, console=console) as live:
                while True:
                    schedule.run_pending()

                    next_run = schedule.next_run()
                    if next_run:
                        remaining_time = (next_run - datetime.now()).total_seconds()
                        remain_hours = int(remaining_time // 3600)
                        remaining_time %= 3600
                        remain_minutes = int(remaining_time // 60)
                        remain_seconds = int(remaining_time % 60)

                        next_run_time_str = next_run.strftime('%H:%M:%S')

                        countdown_text = Text()
                        countdown_text.append(f'距离下次执行任务还有', style='white')
                        countdown_text.append(f'{remain_hours}:{remain_minutes:02d}:{remain_seconds:02d}',
                                              style='bold cyan')
                        countdown_text.append('(将在', style='white')

                        for i, t in enumerate(time_list):
                            if t == next_run_time_str:
                                countdown_text.append(t, style='bold cyan')
                            else:
                                countdown_text.append(t, style='white')
                            if i < len(time_list) - 1:
                                countdown_text.append('、', style='white')

                        countdown_text.append('执行)', style='white')

                        panel = Panel(
                            countdown_text,
                            title='[bold green]定时任务倒计时[/bold green]',
                            border_style='green',
                            padding=(1, 2)
                        )

                        live.update(panel)

                    time.sleep(1)

        return inner

    return decorator
