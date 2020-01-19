#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : mail_sender.py
@Author: HP.Liew
@Date  : 2020/1/7 10:26
@Desc  : 
'''
import smtplib
import time
import re
import os
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from EasyWork.utils.database_ops import *


def getContactEmailAddr(Q_dict):
    '''
    查询用户邮箱地址
    :param Q_dict:查询参数
    :return:用户1 <email1>
    '''

    item = getFilterColumns('contact',Q_dict).values()
    name, email = item[0]['name'], item[0]['email']
    return '{} <{}>'.format(name, email)


def getMulContactEmailAddr(names=None, phones=None, department='基础平台部'):
    '''

    :param names: 用户列表/用户名
    :param phones: 电话号码列表/电话号码
    :param department: 部门
    :return: 用户1 <email1>; 用户2 <email2>;
    '''
    if phones: # 按电话号码查询
        if isinstance(phones, list):
            return ';'.join([getContactEmailAddr({'phone':phone}) for phone in phones])
        if isinstance(phones, str):
            return getContactEmailAddr({'phone':phones})
        print('按电话号码查询时邮箱地址请输入列表或字符串')
        return False
    if names: # 按部门和姓名查询
        if isinstance(names, list):
            return ';'.join([getContactEmailAddr({'name':name, 'department':department}) for name in names])
        if isinstance(names, str):
            return getContactEmailAddr({'name':names, 'department':department})
        print('按用户名查询邮箱地址时请输入列表或字符串')
        return False



def formatEmailAddr(address, sep=';'):
    '''
    显示邮件的收件人，发件人和抄送人的名字
    :param address:邮箱地址格式：显示名 <testor@mail.com>;显示名 <testor@mail.com>;
    :return:解析后的邮箱地址列表
    '''
    address_list = []
    address = address.split(sep)
    for ad in address:
        alias_name, addr = parseaddr(ad)
        address_list.append(formataddr((Header(alias_name, charset="utf-8").encode(), addr)))
    return address_list


def checkInputEmailAddress(email_str):
    '''
    检查邮箱地址正确性
    输入的邮箱地址分隔符只支持英文逗号和分号
    :param email_str:
    :return:
    '''
    email_str_pt = re.compile('^[-a-z0-9.,;@_]$', re.I)
    if not email_str_pt.match(email_str):  # 邮箱字符串不合法
        return '邮箱地址字符串存在非法字符，请确认是否存在中文字符，#、%、*等非法字符'

    if ',' in email_str:
        sep = ','
    else:
        sep = ';'
    email_pattern = re.compile('^[a-z][-a-z0-9.]*@[-a-z0-9]+[.-a-z0-9]*\.(com|cn|net|edu|info)$', re.I)
    mail_address_list = email_str.split(sep)
    for mal in mail_address_list:
        alias, address = parseaddr(mal)
        if not email_pattern.match(address):
            return '邮箱地址格式出错'
    return '邮箱地址校验成功'


def checkEmailLogin(mail_str, password):
    '''
    检查邮箱登陆
    :param mail_str:
    :param password:
    :return:
    '''
    s_smtp = smtplib.SMTP('smtp.chinamobile.com', 25)
    mail_address = parseaddr(mail_str)[-1]
    try:
        s_smtp.login(mail_address, password)
        s_smtp.quit()
        return 'Email checked!'
    except Exception as e:
        print('[ERROR][email login] {}'.format(e))
        return 'Email checked error'


def mailSender(title, recevier, sender, body, sender_mail, sender_pass, cc=None, file_name=None, msg_type='plain'):
    '''
    发送邮件
    :param title: 邮件标题
    :param recevier: 收件人。 邮箱地址格式：显示名 <testor@mail.com>;显示名 <testor@mail.com>;
    :param sender: 发件人。 邮箱地址格式：显示名 <testor@mail.com>;显示名 <testor@mail.com>;
    :param cc: 抄送人。 邮箱地址格式：显示名 <testor@mail.com>;显示名 <testor@mail.com>;
    :param body: 邮件正文
    :param sender_mail: 发送者邮箱。 testor@mail.com
    :param sender_pass: 发送者邮箱密码
    :param file_name: 附件
    :return: 返回是否发送成功
    '''
    print('[INFO] 准备发送 [{}] 邮件'.format(title))
    smtp_server = 'smtp.chinamobile.com'
    msg_root = MIMEMultipart('related')

    msg_root['subject'] = Header(title)
    msg_root['to'] = ','.join(formatEmailAddr(recevier))
    if cc:
        msg_root['cc'] = ','.join(formatEmailAddr(cc))
        recevier = recevier + cc
    msg_root['from'] = ','.join(formatEmailAddr(sender))
    msg_root['date'] = time.ctime()

    b_body = MIMEText(body, msg_type, 'utf-8')
    msg_root.attach(b_body)
    # 如果有附件则添加附件
    if file_name:
        base_name = os.path.split(file_name)[-1]
        part = MIMEApplication(open('{}'.format(file_name), 'rb').read())
        # 解决outlook显示附件为bin
        part.add_header('Content-Disposition', 'attachment', filename=Header(base_name, 'utf-8').encode())
        msg_root.attach(part)

    s_smtp = smtplib.SMTP(smtp_server, 25)
    s_smtp.login(sender_mail, sender_pass)
    try:
        s_smtp.sendmail(sender, recevier, str(msg_root))
        s_smtp.quit()
        print('[INFO] [{}] 邮件发送成功！'.format(title))
        return True
    except Exception as e:
        s_smtp.quit()
        print('[ERROR] 发送 [{}] 邮件遇到一个错误. {}'.format(title, e))
        return False
