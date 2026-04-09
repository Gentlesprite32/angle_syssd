# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/9 14:30
# File:signer.py
import time
import random

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
    def __init__(
            self,
            cookies: str,
            activity_id: str,
            flow_id: str,
            push_key: Optional[str] = None,
            sd_id: Optional[str] = ''.join(random.choices('0123456789abcdef', k=32)),
            special_date: Optional[list] = None,
            special_date_flow_id: Optional[str] = None,
            cumulative_day: Optional[list] = None,
            cumulative_day_flow_id: Optional[str] = None,
            version_gift_activity_id: Optional[str] = None,
            version_gift_play_flow_id: Optional[str] = None,
            version_gift_share_flow_id: Optional[str] = None,
            version_gift_flow_id: Optional[str] = None
    ):
        self.cookies = cookies
        self.session = requests.Session()
        self.update_cookies()
        self.activity_id = activity_id
        self.flow_id = flow_id
        self.push_key = push_key
        self.sd_id = sd_id
        self.special_date = special_date
        self.special_date_flow_id = special_date_flow_id
        self.cumulative_day = cumulative_day
        self.cumulative_day_flow_id = cumulative_day_flow_id
        self.version_gift_activity_id = version_gift_activity_id
        self.version_gfit_play_flow_id = version_gift_play_flow_id
        self.version_gift_share_flow_id = version_gift_share_flow_id
        self.version_gift_flow_id = version_gift_flow_id

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
            'iActivityId': '',  # 由调用方填充。
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
            gift_prefix: str,
            no_package_name: Optional[bool] = False,
            is_success_notify: Optional[bool] = True
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
            self.check_ret(response_data.get('ret'))
            log.info(response_data) if response_data else None
            package_name = response_data.get('modRet', {}).get('jData', {}).get('sPackageName', '')
            p = f'{gift_prefix}:[{token_params.get("roleName", "")}][{token_params.get("areaName", "")}]:'
            if package_name and isinstance(package_name, str):
                try:
                    package_name = package_name.encode('latin1').decode('utf8')
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
                p += package_name
                log.info(p)
                console.log(p)
                self.notify(text=success_text, desp=package_name) if is_success_notify else None
                return True

            s_msg = response_data.get('flowRet', {}).get('sMsg')

            if s_msg and isinstance(s_msg, str):
                s_msg = s_msg.strip('！')
                p += f'{s_msg}。'
                log.info(p)
                console.log(p)
                if no_package_name:
                    if response_data.get('ret', '') in ('600', '700'):  # 600:"对不起您已经领取过了",700:"签到天数不够哦"。
                        return False
                    self.notify(text=success_text) if is_success_notify else None
                    return True
                return False

            msg = response_data.get('msg')
            if msg and isinstance(msg, str):
                p += msg
                log.info(p)
                console.log(p)
                return False

            log.info(response_data)
            console.log(response_data)
            self.notify(text='账号已失效。')
            return False
        except Exception as e:
            log.error(f'{gift_prefix}请求失败,原因:"{e}"')
            self.notify(text=f'{gift_prefix}失败,请查看运行日志。')
            return False

    def get_sign_count(self) -> int:
        try:
            self.update_cookies()

            data = self.get_request_data(self.cumulative_day_flow_id, str(len(self.cumulative_day)))
            data['iActivityId'] = self.activity_id
            url = self.get_request_url(self.activity_id, self.cumulative_day_flow_id, self.sd_id)

            res = self.session.post(url, headers=self.headers, data=data, verify=False)
            response_data = res.json()
            log.info(response_data) if response_data else None
            self.check_ret(response_data.get('ret'))
            sign_data = response_data.get('failedRet')
            if not isinstance(sign_data, dict):  # 最后一个礼包领取成功。
                return self.cumulative_day[-1]
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

    def check_ret(self, ret: Union[str, int]) -> None:
        if not ret:
            return

        if isinstance(ret, int):
            ret: str = str(ret)

        prompt: Union[str, None] = None
        if ret == '101':
            prompt: str = '请先登录。'
        elif ret == '99998':
            prompt: str = '请先绑定大区后重新获取COOKIES并填写。'
        elif ret == '300':
            prompt: str = '活动还未开始。'
        elif ret == '301':
            prompt: str = '活动已结束。'

        if not prompt:
            return

        console.log(prompt)
        self.notify(text=prompt)
        raise SystemExit(-1)

    @staticmethod
    def check_current_date(func):

        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            self: NZSigner = args[0]
            current_date: str = str(datetime.now().date())
            if all((self.special_date, self.special_date_flow_id)):
                if current_date in self.special_date:
                    p = f'"{current_date}"在{self.special_date}限定日期列表中,开始领取限定日期礼包。'
                    log.info(p)
                    console.log(p)
                    self.special_date_gift()
            if all((self.cumulative_day, self.cumulative_day_flow_id)):
                sign_count: int = self.get_sign_count()
                if sign_count == self.cumulative_day[-1]:
                    p = f'"{sign_count}"在{self.cumulative_day}累计签到天数列表中,开始领取签到{sign_count}天礼包。'
                    log.info(p)
                    console.log(p)
                    self.notify(text=f'累计签到{sign_count}天礼包领取成功。')
                elif sign_count != 0:
                    if sign_count in self.cumulative_day:
                        p = f'"{sign_count}"在{self.cumulative_day}累计签到天数列表中,开始领取签到{sign_count}天礼包。'
                        log.info(p)
                        console.log(p)
                        self.cumulative_day_gift(sign_count=sign_count)
                else:
                    p = '没有获取到签到天数,累计签到天数礼包可能已全部领取完成。'
                    log.info(p)
                    console.log(p)
            return result

        return inner

    def cumulative_day_gift(self, sign_count: int):
        num = str(safe_index(obj=self.cumulative_day, value=sign_count, start=1))
        log.info(
            '领取累计签到礼包,'
            f'num:{num},'
            f'flow_id:{self.cumulative_day_flow_id},'
            f'sign_count:{sign_count},'
            f'cumulative_day:{self.cumulative_day}。'
        )
        self.request(
            activity_id=self.activity_id,
            flow_id=self.cumulative_day_flow_id,
            sd_id=self.sd_id,
            num=num,
            success_text=f'累计签到{sign_count}天礼包领取成功。',
            gift_prefix='领取累计签到礼包',
            no_package_name=True
        )

    def special_date_gift(self):
        current_date = str(datetime.now().date())
        num = str(safe_index(obj=self.special_date, value=current_date, start=1))
        log.info(
            f'领取限定日期礼包,'
            f'num:{num},'
            f'flow_id:{self.special_date_flow_id},'
            f'current_date:{current_date},'
            f'special_date:{self.special_date}。'
        )
        self.request(
            activity_id=self.activity_id,
            flow_id=self.special_date_flow_id,
            sd_id=self.sd_id,
            num=num,
            success_text=f'{current_date}限定日期礼包领取成功。',
            gift_prefix='领取限定日期礼包'
        )

    def get_version_gift(
            self,
            delay: Optional[int] = 1
    ):
        if not self.version_gift_activity_id:
            log.info('没有配置版本福利礼包的activity_id。')
            return None

        roll_records: list = []
        log.info(f'获取到版本福利礼包activity_id:"{self.version_gift_activity_id}"。')

        if self.version_gfit_play_flow_id:
            log.info(f'获取到版本福利每日完成一局游戏的flow_id:"{self.version_gfit_play_flow_id}"。')
            roll_records.append(
                self.request(
                    activity_id=self.version_gift_activity_id,
                    flow_id=self.version_gfit_play_flow_id,
                    sd_id=self.sd_id,
                    num='0',
                    success_text='版本福利每日完成一局游戏礼包领取成功。',
                    gift_prefix='领取版本福利每日完成一局游戏礼包',
                    is_success_notify=False
                )
            )

        if self.version_gift_share_flow_id:
            log.info(f'获取到版本福利每日首次分活动的flow_id:"{self.version_gift_share_flow_id}"。')
            roll_records.append(
                self.request(
                    activity_id=self.version_gift_activity_id,
                    flow_id=self.version_gift_share_flow_id,
                    sd_id=self.sd_id,
                    num='0',
                    success_text='版本福利分享礼包领取成功。',
                    gift_prefix='领取版本福利每日首次分享活动礼包',
                    is_success_notify=False
                )
            )

        roll_counts: int = roll_records.count(True)

        if roll_counts == 0:
            log.info('本次领取版本福利未获取到抽奖次数，不再抽取版本福利。')
            return

        if self.version_gift_flow_id:
            success_text: str = '版本福利领取成功。'
            log.info(f'本次获取抽奖次数:{roll_counts}次。')
            gift_records: list = []
            for i in range(roll_counts):
                gift_records.append(
                    self.request(
                        activity_id=self.version_gift_activity_id,
                        flow_id=self.version_gift_flow_id,
                        sd_id=self.sd_id,
                        num='0',
                        success_text=success_text,
                        gift_prefix=f'[{i + 1}/{roll_counts}]领取版本福利礼包',
                        is_success_notify=False
                    )
                )
                if i < roll_counts - 1:
                    time.sleep(delay)
            success_counts: int = gift_records.count(True)
            p = f'版本福利领取结果:[{success_counts}/{roll_counts}]。'
            log.info(p)
            console.log(p)

            if success_counts == 0:
                log.warning('没有资格抽取版本福利奖励。')
                return

            self.notify(text=success_text, desp=p)

    @schedule_task(['00:00:00'])
    @check_current_date
    def sign(self):
        self.request(
            activity_id=self.activity_id,
            flow_id=self.flow_id,
            sd_id=self.sd_id,
            num='-1',
            success_text='签到成功。',
            gift_prefix='领取签到礼包'
        )
        self.get_version_gift()
