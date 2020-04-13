#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : passwd_ops.py
@Author: HP.Liew
@Date  : 2020/1/8 9:17
@Desc  : 
'''
import os
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import base64
from binascii import b2a_hex, a2b_hex

from Crypto import Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

from EasyWork.utils.database_ops import *


def makePasswd(text):
    '''
    使用django自带的密码生成器加密密码
    :param text:
    :return: 加密后的密码字符串
    '''
    return make_password(text)


def checkPasswd(passwd, text):
    '''
    检查密码是否匹配
    :param passwd: 待匹配密码
    :param text: 正确密码加密后的字符串
    :return: True, False
    '''
    return check_password(passwd, text)


def encrypt(passwd, text):
    '''
    使用密码对文本进行对称加密
    :param passwd: 加密密码
    :param text: 加密文本
    :return: 加密后的文本
    '''
    passwd = passwd.encode('utf-8')
    text = text.encode('utf-8')
    cryptor = AES.new(passwd, AES.MODE_CBC, b'0000000000000000')
    text = text + ('\0' * (16 - (len(text) % 16))).encode('utf-8')  # 密钥的长度必须为16Bytes长度的倍数
    cipher_text = cryptor.encrypt(text)
    return str(b2a_hex(cipher_text), encoding='utf-8')


def decrypt(passwd, text):
    '''
    使用对称密码对文本解密
    :param passwd: 加密密码
    :param text: 待机密文本
    :return: 解密后的文本
    '''
    passwd = passwd.encode('utf-8')
    cryptor = AES.new(passwd, AES.MODE_CBC, b'0000000000000000')

    plain_text = cryptor.decrypt(a2b_hex(text))
    plain_text = str(plain_text, encoding='utf-8')
    return plain_text.rstrip('\0')


def genPublickey(prefix):
    '''
    非对称加密，产生公钥发送出去，私钥保存在服务器
    :param prefix: 区分保存的私钥文件名
    :return: 加密公钥
    '''
    # 伪随机数方式生成RSA公私钥对
    random_generator = Random.new().read
    rsa = RSA.generate(1024, random_generator)
    rsa_private_key = rsa.exportKey()
    rsa_public_key = rsa.publickey().exportKey()
    # 存储到静态文件

    with open(os.path.join(settings.CONF_DIR, f'{prefix}_rsa_key.pem'), 'w+') as f:
        f.write(rsa_private_key.decode())
        f.close()
    return rsa_public_key.decode()


def dePrivatekey(password, prefix):
    '''
    还原明文密码
    :param password: 加密的密码
    :param prefix: 私钥文件名前缀
    :return: 返回解密密码
    '''
    key_file = os.path.join(settings.CONF_DIR, f'{prefix}_rsa_key.pem')
    if not os.path.exists(key_file):
        print('私钥文件不存在')
        return False
    with open(key_file, 'r') as f:
        privkeystr = f.read().encode()
        f.close()
    # privkey 为私钥对象，由n，e等数字构成
    privkey = RSA.importKey(privkeystr)
    cipher = PKCS1_v1_5.new(privkey)
    # 现将base64编码格式的password解码，然后解密，并用decode转成str
    password = cipher.decrypt(base64.b64decode(password.encode()), 'error').decode()
    # 至此，password解密成功，省略后面验证用户名和密码的代码了。
    return password


def checkAdmin(passwd):
    '''
    检查超级管理员密码
    :param passwd:
    :return:
    '''
    passwd_str = getSingleData('password', 'name', 'admin', filter='exact').values()[0]['passwd']
    return checkPasswd(passwd, passwd_str)


def getPassword(p_name, passwd=None):
    '''
    从数据库中获取密码。获取的密码都是经过二次加密的密码，还需要解密才能获取到明文密码。
    :param passwd: 解密密码
    :param p_name: 提取的密码
    :return:
    '''
    if not passwd: passwd = getPswd()
    if p_name == 'admin': return False
    passwd_str = getSingleData('password', 'name', p_name, filter='exact').values()[0]['passwd']
    return decrypt(passwd, passwd_str)


def insertPassword(text, p_name, passwd=None, note=''):
    '''
    将密码加密后，存放到数据库中
    :param passwd: 加密密码
    :param text: 入库密码
    :param p_name: 入库密码名称
    :param note: 密码备注
    :return: 插入结果
    '''
    if not passwd: passwd = getPswd()
    passwd_str = encrypt(passwd, text)
    datas = [{'name': p_name, 'note': note, 'passwd': passwd_str}]
    try:
        insertBulk('password', datas)
    except Exception as e:
        print(f'插入密码[{text}]失败。{e}')
        return False
    return True


def updatePassword(text, p_name, passwd=None, note=''):
    '''
    更新单个密码
    :param passwd: 加密密码
    :param text: 待更新入库密码
    :param p_name: 待更新入库密码名称
    :param note: 密码备注
    :return:
    '''
    if not passwd: passwd = getPswd()
    if p_name == 'admin':  # 超级密码更新，则所有密码都要更新
        if not checkAdmin(passwd): return False
        datas = getAll('password').values()
        for pd in datas:
            if pd['name'] == 'admin':
                pd['passwd'] = makePasswd(text)
            else:
                pd['passwd'] = encrypt(text, getPassword(passwd, pd['name']))
    else:  # 单独更新密码
        passwd = encrypt(passwd, text)
        datas = [{'name': p_name, 'note': note, 'passwd': passwd}]
    try:
        updateBulk('password', datas, 'name')
    except Exception as e:
        print(f'更新密码[{text}]失败。{e}')


def getPswd():
    return open(os.path.join(settings.TEST_DIRS, 'config', 'passwd'), 'r').read().strip()
