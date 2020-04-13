#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : sox_remainder.py
@Author: HP.Liew
@Date  : 2020/1/13 10:16
@Desc  : 根据SOX内控矩阵，提取出需要主动出具材料的控制点，筛查出定期执行的控制点。以责任人划分执行以下操作：
         不定期、定期和系统控制的点不提醒
         每天和每周执行的任务每月第一个工作日提醒
         每月第一个工作日提醒
         每季度第一个工作日提醒
         每半年第一个工作日提醒
         每年第一个工作日提醒
'''
import datetime
from django.conf import settings
from EasyWork.utils.database_ops import *
from EasyWork.utils.date_utils import getMonthFirstWeekDay
from EasyWork.utils.mail_utils import mailSender
from EasyWork.utils.config import Config


def _updateSoxTaskTable(date_str):
    '''
    查询SOX表的内容，找出主动提供材料且为周期性执行的控制点，提取控制点编号、频率、描述、测试资料、关注点
    将查询到的数据经过分析后，插入到SOX任务表中
    :param date_str: 提取指定日期的数据
    :return:{'user':[{'point':'stand_point',...},...],...}
    '''
    result = []  # 责任人：[控制点相关信息]
    if not isinstance(date_str, datetime.date):
        print('请输入datetime.date类型的日期')
        return False
    Q_dict = {'frequency': '每', 'action': '主动', 'update': date_str}
    items = getFilterColumns('sox', Q_dict).values()
    year, month = datetime.date.today().year, datetime.date.today().month
    for item in items:
        staffs = item['staff'].split(',')
        item_dict = {'point': item['stand_point'], 'frequency': item['frequency'], 'describe': item['company_describe'],
                     'test_file': item['test_file'], 'focus': item['focus_point']}
        # 初始化本次执行时间
        item_dict['exec_date'] = datetime.date.today()
        # 计算下次任务执行时间
        if '每季度' in item['frequency']:
            season = ((month - 1) // 3 + 1) * 3
            item_dict['next_exec_date'] = getMonthFirstWeekDay(season)
        elif '每半年' in item['frequency']:
            half_year = ((month - 1) // 6 + 1) * 6
            item_dict['next_exec_date'] = getMonthFirstWeekDay(half_year)
        elif '每年' in item['frequency']:
            item_dict['next_exec_date'] = getMonthFirstWeekDay(1, year)
        else:
            item_dict['next_exec_date'] = getMonthFirstWeekDay(month)

        for staff in staffs:
            item_dict['staff'] = staff
            result.append(item_dict.copy())
    try:
        importDatabase('soxtasks', result, dropTable=True)
    except Exception as e:
        print('重新编排SOX定期执行任务时，插入数据库出错。{}'.format(e))


def _updateTask(point_list):
    '''
    更新SOX任务表，仅更新需要人工控制的控制点，系统控制的控制点不需要提醒。
    :param point_list: soxtasks数据
    :return:
    '''
    date_str = datetime.date.today()
    year, month = date_str.year, date_str.month
    for item in point_list:
        item['exec_date'] = date_str
        if '每季度' in item['frequency']:
            season = ((month + 3 - 1) // 3 + 1) * 3
            item['next_exec_date'] = getMonthFirstWeekDay(month=season)
        elif '每半年' in item['frequency']:
            half_year = ((month + 6 - 1) // 6 + 1) * 6
            item['next_exec_date'] = getMonthFirstWeekDay(month=half_year)
        elif '每年' in item['frequency']:
            item['next_exec_date'] = getMonthFirstWeekDay(month=1, year=year + 1)
        else:
            item['next_exec_date'] = getMonthFirstWeekDay(month=month + 1)
        print('更新{}数据，责任人{}'.format(item['point'], item['staff']))
        updateSingle('soxtasks', item, ['staff', 'point'])


def _getContact(name, department):
    '''
    获取联系人信息
    :param name:联系人中文名字
    :param department:联系人所在的部门
    :return:
    '''
    contact = getFilterColumns('contact', {'name': name, 'department': department}).values()
    if not contact:
        print('通讯录中没有找到联系人{}'.format(name))
        return
    return contact[0]


def soxReminder(update_sox=False):
    '''
    找出所有计划执行时间小于今天执行的任务，并以责任人合并，生成邮件，提醒责任人执行控制点要求。
    同时，根据情况更新计划任务表
    :param update_sox: 先更新SOXTASKS表后执行
    :return:
    '''
    configer = Config('sox.ini')
    date_str = configer.getRaw('sox_mail', 'updatestr')
    sender = configer.getRaw('sox_mail', 'sender')
    sender_pass = configer.getRaw('sox_mail', 'senderpass')
    department = configer.getRaw('sox_mail', 'department')
    cc = re.split('[,，]', configer.getRaw('sox_mail', 'cc'))
    sender_autograph = configer.getRaw('sox_mail', 'autograph')
    if update_sox:
        if not date_str:
            print('请指明基准数据的导入日期')
            return
        else:
            print(f'更新{date_str}的数据为基准数据')
        _updateSoxTaskTable(date_str)
    # 提取抄送人
    if cc[0]:  # re 切分肯定有list结果，但是不一定有数据
        cc_list = []
        for c in cc:
            c = _getContact(c, department)
            if c: cc_list.append('{} <{}>'.format(c['name'], c['email']))
        cc = ';'.join(cc_list)

    result = {}
    today_str = datetime.date.today()
    items = getFilterColumns('soxtasks', {'next_exec_date': today_str}, filter='lte').values()
    # 按责任人分类
    if not items: return
    for item in items:
        staff = item['staff']
        if staff not in result:
            result[staff] = [item]
        else:
            result[staff].append(item)
    if not result: return
    # 生成发件人信息
    contact = _getContact(sender, department)
    if contact:
        sender_mail = contact['email']
    else:
        print('发件人通讯录信息获取失败')
        return
    print('准备发送提醒邮件！')
    sender = '{} <{}>'.format(sender, sender_mail)
    title = '{}年{:0>2}月基础平台部SOX内控矩阵执行提醒！'.format(today_str.year, today_str.month)

    # 生成邮件内容
    for staff, items in result.items():
        point_list = []
        # 生成收件人地址信息
        contact = _getContact(staff, department)
        if contact:
            recevier = '{} <{}>'.format(staff, contact['email'])
        else:
            print('收件人通讯录信息获取失败')
            continue
        # 邮件内容
        content = []
        for idx, item in enumerate(items):
            point_list.append(item)
            item_content = '''
                <p><span><b>&nbsp;&nbsp;&nbsp;&nbsp;{}. 控制点：</b>{}</span></p>
                <p><span><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;频率：</b>{}</span></p>
                <p><span><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;测试资料：</b>{}</span></p>
                <p><span><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;关注点：</b>{}</span></p>
                <p><span><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;控制点描述：</b>{}</span></p>''' \
                .format(idx + 1, item['point'], item['frequency'], item['test_file'], item['focus'], item['describe'])
            content.append(item_content)
        mail_body = '''<html><body><div style='font-size:12.0pt;font-family:宋体;'>
            <p><span>{}：</span></p><p><span>&nbsp;&nbsp;&nbsp;&nbsp;你好！</span></p>
            <p><span>&nbsp;&nbsp;&nbsp;&nbsp;根据SOX内控审计要求，你名下有以下控制点需要在本月执行，请及时执行。</span></p>
            {}{}</div></body></html>'''.format(staff[-2:], '\n'.join(content), sender_autograph)

        # # print(title, recevier, sender, mail_body, sender_mail, sender_pass)
        # 邮件发送成功后更新sox任务表，计算下次执行时间。
        if mailSender(title, recevier, sender, mail_body, sender_mail, sender_pass, msg_type='html', cc=cc):
            _updateTask(point_list)


# soxReminder()
