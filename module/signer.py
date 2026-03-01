# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:30
# File:signer.py
import time

from functools import wraps
from datetime import datetime
from typing import (
    Union,
    Optional
)

import requests
import contextlib
from urllib.parse import (
    unquote_plus,
    parse_qs
)

from . import log, console
from .util import (
    safe_index,
    schedule_task,
    sc_send
)


class NZSigner:
    def __init__(self, cookies: str, push_key: Union[str, None] = None):
        self.cookies = cookies
        self.session = requests.Session()
        self.update_cookies()
        self.push_key = push_key

    def update_cookies(self):
        """更新会话的Cookies"""
        _cookies = {}
        for c in self.cookies.split(';'):
            with contextlib.suppress(Exception):
                k, v = c.strip().split('=', 1)
                _cookies[k] = v
        self.session.cookies.update(_cookies)

    def parse_token_params(self) -> dict:
        token_params_str = unquote_plus(unquote_plus(self.session.cookies.get('tokenParams', '')))
        return {k: v[0] for k, v in parse_qs(token_params_str).items()}

    def notify(self, text, desp=''):
        sc_send(text=text, desp=desp, key=self.push_key) if self.push_key else None

    def get_request_data(self, flow_id: str, num: str = '-1') -> dict:
        """构造请求数据。"""
        token_params = self.parse_token_params()
        return {
            'appid': '1104904086',
            'num': num,
            'userId': token_params.get('userId', ''),
            'tokenId': token_params.get('token', ''),
            'iActivityId': '',  # 由调用方填充
            'iFlowId': flow_id,
            'g_tk': '1842395457',
            'e_code': '0',
            'g_code': '0',
            'eas_url': 'http://nz.qq.com/cp/a20240816septzs/',
            'eas_refer': 'http://noreferrer/?reqid=41d32ba3-a767-416e-bc52-462a43385af7',
            'version': '27',
            'sServiceDepartment': 'group_a',
            'sServiceType': 'nz'
        }

    def get_request_url(self, activity_id: str, flow_id: str, sd_id: str) -> str:
        """构造请求URL。"""
        current_timestamp = str(int(time.time()))
        token_params = self.parse_token_params()
        return f'https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=nz&iActivityId={activity_id}&sServiceDepartment=group_a&sSDID={sd_id}&sMiloTag=AMS-MILO-{activity_id}-{flow_id}-{token_params.get("userId", "")}-{current_timestamp + "287"}-0poxQT&_={current_timestamp + "288"}'

    @property
    def headers(self) -> dict:
        """构造请求头。"""
        return {
            'Host': 'comm.ams.game.qq.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nz.qq.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1008/3.15.30032.2103150032',
            'Referer': 'https://nz.qq.com/'
        }

    def request(
            self,
            activity_id: str,
            flow_id: str,
            sd_id: str,
            num: str,
            success_text: str,
            error_prefix: str,
            desp_text: Optional[str] = None
    ) -> bool:
        """发送请求并处理响应。"""
        self.update_cookies()
        token_params = self.parse_token_params()

        data = self.get_request_data(flow_id, num)
        data['iActivityId'] = activity_id
        url = self.get_request_url(activity_id, flow_id, sd_id)

        try:
            res = self.session.post(url, headers=self.headers, data=data, verify=False)
            response_data = res.json()
            log.info(response_data) if response_data else None
            package_name = response_data.get('modRet', {}).get('jData', {}).get('sPackageName', '')
            p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:'
            log.info(response_data)
            if package_name:
                p += package_name
                log.info(p)
                console.log(p)
                self.notify(text=success_text, desp=package_name if desp_text is None else desp_text)
                return True

            msg = response_data.get('msg')
            if msg:
                p += msg
                log.info(p)
                console.log(p)
                return False
            else:
                p = response_data
                log.info(p)
                console.log(p)
                self.notify(text='账号已失效。')
                return False
        except Exception as e:
            log.error(f'{error_prefix}请求失败,原因"{e}"')
            self.notify(text=f'{error_prefix}失败,请查看运行日志。')
            return False

    def get_sign_count(
            self,
            activity_id: str,
            cumulative_day_flow_id: str,
            sd_id: str
    ) -> int:
        try:
            self.update_cookies()

            data = self.get_request_data(cumulative_day_flow_id, '1')
            data['iActivityId'] = activity_id
            url = self.get_request_url(activity_id, cumulative_day_flow_id, sd_id)

            res = self.session.post(url, headers=self.headers, data=data, verify=False)
            response_data = res.json()
            log.debug(response_data) if response_data else None
            sign_data = response_data.get('failedRet')
            if not isinstance(sign_data, dict):
                return 0
            cond_rets = []
            for data in sign_data.values():
                try:
                    cond_ret = data['jRuleFailedInfo']['iCondRet']
                    cond_rets.append(cond_ret)
                except (KeyError, TypeError):
                    continue
            if cond_rets:
                sign_count = cond_rets[0]
                p = f'累计签到{sign_count}天。'
                log.info(p)
                console.log(p)
                return int(sign_count)
            return 0
        except Exception as e:
            log.error(f'无法获取累计签到天数,原因:"{e}"')
            return 0

    @staticmethod
    def check_current_date(func):

        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            activity_id: str = kwargs.get('activity_id')
            sd_id: str = kwargs.get('sd_id')
            special_date: Union[str, None] = kwargs.get('special_date')
            special_date_flow_id: Union[str, None] = kwargs.get('special_date_flow_id')
            cumulative_day: Union[list, None] = kwargs.get('cumulative_day')
            cumulative_day_flow_id: Union[str, None] = kwargs.get('cumulative_day_flow_id')
            current_date: str = str(datetime.now().date())
            self: NZSigner = args[0]
            if all((special_date, special_date_flow_id)):
                if current_date in special_date:
                    p = f'"{current_date}"在{special_date}限定日期列表中,开始领取限定日期礼包。'
                    log.info(p)
                    console.log(p)
                    self.special_date_gift(
                        activity_id=activity_id,
                        special_date_flow_id=special_date_flow_id,
                        sd_id=sd_id,
                        special_date=special_date
                    )
            if all((cumulative_day, cumulative_day_flow_id)):
                sign_count: int = self.get_sign_count(
                    activity_id=activity_id,
                    cumulative_day_flow_id=cumulative_day_flow_id,
                    sd_id=sd_id
                )
                if sign_count != 0:
                    if sign_count in cumulative_day:
                        p = f'"{sign_count}"在{cumulative_day}累计签到天数列表中,开始领取签到{sign_count}天礼包。'
                        log.info(p)
                        console.log(p)
                        self.cumulative_day_gift(
                            activity_id=activity_id,
                            cumulative_day_flow_id=cumulative_day_flow_id,
                            sd_id=sd_id,
                            cumulative_day=cumulative_day,
                            sign_count=sign_count
                        )
            return result

        return inner

    def cumulative_day_gift(
            self,
            activity_id: str,
            cumulative_day_flow_id: str,
            sd_id: str,
            cumulative_day: list,
            sign_count: int
    ):
        num = str(safe_index(obj=cumulative_day, value=sign_count, start=1))
        log.info(
            f'领取累计签到礼包,'
            f'num:{num},'
            f'flow_id:{cumulative_day_flow_id},'
            f'sign_count:{sign_count},'
            f'cumulative_day:{cumulative_day}。'
        )
        self.request(
            activity_id=activity_id,
            flow_id=cumulative_day_flow_id,
            sd_id=sd_id,
            num=num,
            success_text=f'{cumulative_day_flow_id}累计签到礼包领取成功。',
            error_prefix='领取累计签到礼包'
        )

    def special_date_gift(
            self,
            activity_id: str,
            special_date_flow_id: str,
            sd_id: str,
            special_date: Optional[list] = None
    ):
        current_date = str(datetime.now().date())
        num = str(safe_index(obj=special_date, value=current_date, start=1))
        log.info(
            f'领取限定日期礼包,'
            f'num:{num},'
            f'flow_id:{special_date_flow_id},'
            f'current_date:{current_date},'
            f'special_date:{special_date}。'
        )
        self.request(
            activity_id=activity_id,
            flow_id=special_date_flow_id,
            sd_id=sd_id,
            num=num,
            success_text=f'{special_date}限定日期礼包领取成功。',
            error_prefix='领取限定日期礼包'
        )

    @schedule_task(['00:00:00'])
    @check_current_date
    def sign(
            self,
            activity_id: str,
            flow_id: str,
            sd_id: str,
            special_date: Optional[list] = None,
            special_date_flow_id: Optional[str] = None,
            cumulative_day: Optional[list] = None,
            cumulative_day_flow_id: Optional[str] = None
    ):
        self.request(
            activity_id=activity_id,
            flow_id=flow_id,
            sd_id=sd_id,
            num='-1',
            success_text='签到成功。',
            error_prefix='领取签到礼包'
        )
