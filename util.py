# coding=UTF-8
# Author:Gentlesprite
# Software:PyCharm
# Time:2025/9/11 16:14
# File:util.py
from typing import Hashable, Union, Optional


def safe_index(
        obj: Union[list, None],
        value: Hashable,
        start: Optional[int] = 0
) -> Union[int, None]:
    try:
        return obj.index(value) + start
    except (ValueError, AttributeError):
        return None
