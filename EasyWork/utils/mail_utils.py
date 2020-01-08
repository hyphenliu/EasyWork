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


def formatEmailAddr(address, sep=';'):
    '''
    显示邮件的收件人，发件人和抄送人的名字
    :param persons:
    :return:
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
    :param email_str:
    :return:
    '''
    if ',' in email_str:
        sep = ','
    else:
        sep = ';'
    email_pattern = re.compile('^[a-z][-a-z0-9.]*@[-a-z0-9]+[.-a-z0-9]*\.(com|cn|net|edu|info)$', re.I)
    mail_address_list = email_str.split(sep)
    for mal in mail_address_list:
        alias, address = parseaddr(mal)
        if not email_pattern.match(address):
            return 'Mail address error'
    return 'Mail address checked'


def checkEmail(mail_str, password):
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


def mailSender(title, recevier, sender, cc, body, sender_mail, sender_pass, file_name=None):
    '''
    发送邮件
    :return: 返回是否发送成功
    '''
    print('[INFO] Prepare send [{}] email'.format(title))
    smtp_server = 'smtp.chinamobile.com'
    msg_root = MIMEMultipart('related')

    msg_root['subject'] = Header(title)
    msg_root['to'] = ','.join(recevier)
    msg_root['cc'] = ','.join(cc)
    msg_root['from'] = sender
    msg_root['date'] = time.ctime()

    b_body = MIMEText(body, 'plain', 'utf-8')
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
        s_smtp.sendmail(sender, recevier + cc, str(msg_root))
        s_smtp.quit()
        print('[INFO] [{}] Email sent!'.format(title))
        return True
    except Exception as e:
        s_smtp.quit()
        print('[ERROR] Send [{}] email encounter en error. {}'.format(title, e))
        return False
