#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : wx_reminder.py
@Author: HP.Liew
@Date  : 2020/2/12 15:10
@Desc  : 
'''
import requests
import json
import logging
from EasyWork.utils.config import Config

BASEURL = 'http://wxpusher.zjiecode.com/api'
logger = logging.getLogger('error')


def wechatSender(message):
    '''
    通过http://wxpusher.zjiecode.com/api接口发送微信提醒消息
    返回消息结构：
        {"code":1000,
        "msg":"处理成功",
        "data":[{"uid":"UID_Qw8qPPhbzFzgK9WKrhXPk25eULe1",
                 "topicId":null,
                 "messageId":3426980,
                 "code":1000,
                 "status":"创建发送任务成功"}],
        "success":true}
    :param message: 发送消息内容
    :return: 没有返回结果
    '''
    configer = Config('config.ini')
    appToken = configer.get('wxpusher','appToken')
    uid = configer.get('wxpusher','uid')
    if not message.strip():
        print('发送消息为空，拒绝发送!')
        logger.error('发送消息为空，拒绝发送!')
        return
    try:
        resp = requests.get(f'{BASEURL}/send/message/?content={message}&appToken={appToken}&uid={uid}')
        resp_json = json.loads(resp.text)
        if resp_json.get('code') == 1000:
            logger.info(f'消息发送成功 [{message}]')
        else:
            logger.error(f'消息发送失败, 原因: {resp.text}')
    except requests.exceptions.RequestException as req_error:
        logger.error(f'消息发送请求失败: {req_error}')
    except Exception as e:
        logger.error(f'消息发送失败 [text: {message}]: {e}')
