# from dailywork.utils.database_ops import *
from django.core.cache import cache
from random import randint
import math
import datetime

from EasyWork.utils.database_ops import *


def taxiListGen(per_limit, total_limit, day_list):
    result = []
    if per_limit == 0 or total_limit == 0:
        return None
    total_number = int(math.ceil(1.0 * total_limit / per_limit))  # 计算总单位量
    per_limit = int(total_limit / total_number)  # 根据总单位量和总额度，修改平均数
    members = int(math.ceil(1.0 * total_number / 6))
    for i in range(members):
        if total_number > 6:
            rst = zip(genDate(day_list), genTime(), genLimit(per_limit))
            total_number -= 6
        else:
            rst = zip(genDate(day_list, total_number), genTime(total_number), genLimit(per_limit, total_number))
        for r in rst:
            result.append(list(r))
    return result


def genDate(day_list, number=6):
    '''

    :param day_list:
    :param number:
    :return:
    '''
    date_list = []
    num = 0
    while num < number:
        date_str = day_list[randint(0, len(day_list) - 1)]
        if date_str not in date_list:
            date_str = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            date_list.append(date_str)
            num += 1
    return sorted(date_list)


def genTime(number=6):
    '''
    返回正常上下班时间随机数
    :param number:
    :return: ['hh:MM',...]
    '''
    num = 0
    timelist = []
    while num < number:
        while True:
            hourstr = randint(9, 16)
            if not hourstr in [12, 13]:
                break
        minutestr = randint(0, 59)
        num += 1
        # timelist.append(str(hourstr) + ':' + str(minutestr))
        timelist.append('%02d:%02d' % (hourstr, minutestr))
    return timelist


def genLimit(per_limit, number=6):
    '''
    :param limit:
    :return:
    '''
    num = 0
    sum = 0
    limit_list = []
    min = int(per_limit * 0.95)
    max = int(per_limit * 1.05)
    while num < number - 1:
        price = randint(min, max) + randint(0, 1) * 0.5
        limit_list.append(price)
        num += 1
        sum += price
    # 为确保每个人的额度大于输入额度，最后一行进行调整
    last = int(per_limit * number - sum)
    final = randint(last, last + 2) + randint(0, 1) * 0.5
    if final > max or final < min:  # 不符合要求则重新生成
        return genLimit(per_limit, number)
    else:
        limit_list.append(final)

    return limit_list
