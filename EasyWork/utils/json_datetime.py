#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : json_datetime.py
@Author: HP.Liew
@Date  : 2019/7/30 18:11
@Desc  : 
'''

import json
from datetime import date, datetime


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)
