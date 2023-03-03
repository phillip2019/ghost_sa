# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    鬼策埋点自定义异常模块.
"""


class SnifferException(Exception):
    """嗅探流量只请求，未提供内容，定制此异常，返回200，空内容
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)