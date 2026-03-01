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
    Callable,
    Optional
)

import requests
import contextlib
from urllib.parse import (
    unquote_plus,
    parse_qs
)

from module import log, console
from module.notify import sc_send
from module.util import safe_index


class NZSigner:
    def __init__(self, cookies: str, push_key: Union[str, None] = None):
        self.cookies = cookies
        self.session = requests.Session()
        self.__update_cookies()
        self.push_key = push_key

    def __update_cookies(self):
        """更新会话的Cookies"""
        _cookies = {}
        for c in self.cookies.split(';'):
            with contextlib.suppress(Exception):
                k, v = c.strip().split('=', 1)
                _cookies[k] = v
        self.session.cookies.update(_cookies)

    def __parse_token_params(self) -> dict:
        token_params_str = unquote_plus(unquote_plus(self.session.cookies.get('tokenParams', '')))
        return {k: v[0] for k, v in parse_qs(token_params_str).items()}

    def __process_notify(self, text, desp=''):
        if self.push_key:
            sc_send(text=text, desp=desp, key=self.push_key)

    def get_sign_count(
            self,
            activity_id: str,
            cumulative_day_flow_id: str,
            sd_id: str
    ) -> int:
        try:
            self.__update_cookies()
            current_timestamp = str(int(time.time()))
            token_params = self.__parse_token_params()
            data = {
                'appid': '1104904086',
                'num': '1',
                'userId': token_params.get('userId', ''),
                'tokenId': token_params.get('token', ''),
                'iActivityId': activity_id,
                'iFlowId': cumulative_day_flow_id,
                'g_tk': '1842395457',
                'e_code': '0',
                'g_code': '0',
                'eas_url': 'http://nz.qq.com/cp/a20240816septzs/',
                'eas_refer': 'http://noreferrer/?reqid=41d32ba3-a767-416e-bc52-462a43385af7',
                'version': '27',
                'sServiceDepartment': 'group_a',
                'sServiceType': 'nz'
            }

            url = f'https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=nz&iActivityId={activity_id}&sServiceDepartment=group_a&sSDID={sd_id}&sMiloTag=AMS-MILO-{activity_id}-{cumulative_day_flow_id}-{token_params.get("userId", "")}-{current_timestamp + "287"}-0poxQT&_={current_timestamp + "288"}'

            headers = {
                'Host': 'comm.ams.game.qq.com',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://nz.qq.com',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1008/3.15.30032.2103150032',
                'Referer': 'https://nz.qq.com/'
            }

            res = self.session.post(url, headers=headers, data=data, verify=False)
            response_data = res.json()
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
        self.__update_cookies()
        current_timestamp = str(int(time.time()))
        token_params = self.__parse_token_params()
        data = {
            'appid': '1104904086',
            'num': safe_index(obj=cumulative_day, value=sign_count, start=1),
            'userId': token_params.get('userId', ''),
            'tokenId': token_params.get('token', ''),
            'iActivityId': activity_id,
            'iFlowId': cumulative_day_flow_id,
            'g_tk': '1842395457',
            'e_code': '0',
            'g_code': '0',
            'eas_url': 'http://nz.qq.com/cp/a20240816septzs/',
            'eas_refer': 'http://noreferrer/?reqid=41d32ba3-a767-416e-bc52-462a43385af7',
            'version': '27',
            'sServiceDepartment': 'group_a',
            'sServiceType': 'nz'
        }

        url = f'https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=nz&iActivityId={activity_id}&sServiceDepartment=group_a&sSDID={sd_id}&sMiloTag=AMS-MILO-{activity_id}-{cumulative_day_flow_id}-{token_params.get("userId", "")}-{current_timestamp + "287"}-0poxQT&_={current_timestamp + "288"}'

        headers = {
            'Host': 'comm.ams.game.qq.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nz.qq.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1008/3.15.30032.2103150032',
            'Referer': 'https://nz.qq.com/'
        }

        try:
            res = self.session.post(url, headers=headers, data=data, verify=False)
            response_data = res.json()
            response_len = len(response_data)
            if response_len == 4:  # 签到天数不够。
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:{response_data.get("msg")}'
                log.info(p)
                console.log(p)
            elif response_len > 4:  # 累计签到礼包领取成功。
                package_name = response_data.get('modRet', {}).get('jData', {}).get('sPackageName', '')
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:累计签到礼包领取成功!{package_name}'
                log.info(p)
                console.log(p)
                self.__process_notify(text=f'{cumulative_day_flow_id}累计签到礼包领取成功。', desp=package_name)
            else:
                p = f'{response_data},长度:{response_len}'
                log.info(p)
                console.log(p)
                self.__process_notify(text='账号已失效。')
        except Exception as e:
            log.error(f'领取累计签到礼包请求失败,原因"{e}"')
            self.__process_notify(text='领取累计签到礼包失败,请查看运行日志。')
            return None

    def special_date_gift(
            self,
            activity_id: str,
            special_date_flow_id: str,
            sd_id: str,
            special_date: Optional[list] = None
    ):
        self.__update_cookies()
        current_timestamp = str(int(time.time()))
        token_params = self.__parse_token_params()
        data = {
            'appid': '1104904086',
            'num': str(safe_index(obj=special_date, value=str(datetime.now().date()), start=1)),
            'userId': token_params.get('userId', ''),
            'tokenId': token_params.get('token', ''),
            'iActivityId': activity_id,
            'iFlowId': special_date_flow_id,
            'g_tk': '1842395457',
            'e_code': '0',
            'g_code': '0',
            'eas_url': 'http://nz.qq.com/cp/a20240816septzs/',
            'eas_refer': 'http://noreferrer/?reqid=41d32ba3-a767-416e-bc52-462a43385af7',
            'version': '27',
            'sServiceDepartment': 'group_a',
            'sServiceType': 'nz'
        }

        url = f'https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=nz&iActivityId={activity_id}&sServiceDepartment=group_a&sSDID={sd_id}&sMiloTag=AMS-MILO-{activity_id}-{special_date_flow_id}-{token_params.get("userId", "")}-{current_timestamp + "287"}-0poxQT&_={current_timestamp + "288"}'

        headers = {
            'Host': 'comm.ams.game.qq.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nz.qq.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1008/3.15.30032.2103150032',
            'Referer': 'https://nz.qq.com/'
        }

        try:
            res = self.session.post(url, headers=headers, data=data, verify=False)
            response_data = res.json()
            response_len = len(response_data)
            if response_len == 4:  # 不在领取时间内。
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:{response_data.get("msg")}'
                log.info(p)
                console.log(p)
            elif response_len > 4:  # 限定日期礼包领取成功。
                package_name = response_data.get('modRet', {}).get('jData', {}).get('sPackageName', '')
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:限定日期礼包领取成功!{package_name}'
                log.info(p)
                console.log(p)
                self.__process_notify(text=f'{special_date}限定日期礼包领取成功。', desp=package_name)
            else:
                p = f'{response_data},长度:{response_len}'
                log.info(p)
                console.log(p)
                self.__process_notify(text='账号已失效。')
        except Exception as e:
            log.error(f'领取限定日期礼包请求失败,原因"{e}"')
            self.__process_notify(text='领取限定日期礼包失败,请查看运行日志。')
            return None

    @check_current_date
    def sign(
            self,
            activity_id: str,
            flow_id: str,
            sd_id: str,
            special_date: Optional[list] = None,
            special_date_flow_id: Optional[str] = None,
            cumulative_day: Optional[list] = None,
            cumulative_day_flow_id: Optional[str] = None,
            handler: Optional[Callable] = None
    ):
        self.__update_cookies()
        current_timestamp = str(int(time.time()))
        token_params = self.__parse_token_params()

        data = {
            'appid': '1104904086',
            'num': '-1',
            'userId': token_params.get('userId', ''),
            'tokenId': token_params.get('token', ''),
            'iActivityId': activity_id,
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

        url = f'https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=nz&iActivityId={activity_id}&sServiceDepartment=group_a&sSDID={sd_id}&sMiloTag=AMS-MILO-{activity_id}-{flow_id}-{token_params.get("userId", "")}-{current_timestamp + "287"}-0poxQT&_={current_timestamp + "288"}'

        headers = {
            'Host': 'comm.ams.game.qq.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://nz.qq.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1008/3.15.30032.2103150032',
            'Referer': 'https://nz.qq.com/'
        }

        try:
            res = self.session.post(url, headers=headers, data=data, verify=False)
            response_data = res.json()
            response_len = len(response_data)
            if response_len == 4:  # 已签到。
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:{response_data.get("msg")}'
                log.info(p)
                console.log(p)
            elif response_len > 4:  # 签到成功。
                package_name = response_data.get('modRet', {}).get('jData', {}).get('sPackageName', '')
                p = f'[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:签到成功!{package_name}'
                log.info(p)
                console.log(p)
                self.__process_notify(text='签到成功。', desp=package_name)
            else:
                p = f'{response_data},长度:{response_len}'
                log.info(p)
                console.log(p)
                self.__process_notify(text='账号已失效。')
        except Exception as e:
            log.error(f'领取签到礼包请求失败,原因"{e}"')
            self.__process_notify(text='领取签到礼包请求失败,请查看运行日志。')
            return None
        handler(
            func=self.sign,
            activity_id=activity_id,
            flow_id=flow_id,
            sd_id=sd_id,
            special_date=special_date,
            special_date_flow_id=special_date_flow_id,
            cumulative_day=cumulative_day,
            cumulative_day_flow_id=cumulative_day_flow_id,
            handler=handler
        ) if handler else None
