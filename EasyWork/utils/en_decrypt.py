#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : en_decrypt.py
@Author: HP.Liew
@Date  : 2020/1/8 9:17
@Desc  : 
'''
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

def encrypt(passwd, text):
    passwd = passwd.encode('utf-8')
    text = text.encode('utf-8')
    cryptor = AES.new(passwd, AES.MODE_CBC, passwd)
    text = text + ('\0' * (16 - (len(text) % 16))).encode('utf-8')  # 密钥的长度必须未16Bytes长度的倍数
    cipher_text = cryptor.encrypt(text)
    return b2a_hex(cipher_text)


def decrypt(passwd, text):
    passwd = passwd.encode('utf-8')
    cryptor = AES.new(passwd, AES.MODE_CBC, passwd)
    plain_text = cryptor.decrypt(a2b_hex(text))
    plain_text = str(plain_text, encoding='utf-8')
    return plain_text.rstrip('\0')