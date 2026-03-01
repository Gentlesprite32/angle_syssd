# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2026/1/23 17:47
# File:parser.py
from argparse import (
    ArgumentParser,
    SUPPRESS
)

from module import (
    __version__,
    SOFTWARE_SHORT_NAME
)


class NHSArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            '-h', '--help',
            action='help',
            default=SUPPRESS,
            help='展示帮助'
        )
        self.add_argument(
            '-v', '--version',
            action='version',
            version=f'{SOFTWARE_SHORT_NAME} {__version__}',
            default=SUPPRESS,
            help='展示版本信息'
        )
        self.add_argument(
            '-l', '--loop',
            action='store_true',
            default=False,
            help='循环执行签到任务'
        )


PARSE_ARGS = NHSArgumentParser(add_help=False).parse_args()
