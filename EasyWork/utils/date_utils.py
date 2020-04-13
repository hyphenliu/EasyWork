#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : date_utils.py
@Author: HP.Liew
@Date  : 2020/1/13 16:18
@Desc  : 
'''
import datetime
import re
from EasyWork.utils.config import Config
from django.conf import settings


def getMonthFirstWeekDay(month, year=None):
    '''
    返回给定月份的第一个工作日
    :param month:
    :return:
    '''
    if not year:
        year = datetime.date.today().year
    for i in range(1, 31):
        if isWeekDay(year, month, i):
            return datetime.date(year, month, i)


def isWeekDay(year, month, day):
    '''
    判断给定日期是否为工作日
    :param month:
    :return:
    '''
    configer = Config('holiday.ini')
    holidays = re.split('[,，]', configer.get('holiday', str(year)))
    holidays = [f'{year}-{hd}' for hd in holidays]
    date_str = '{}-{:0>2}-{:0>2}'.format(year, month, day)

    if date_str in holidays:
        return False
    if datetime.date(year, month, day).weekday() < 5:
        return True
