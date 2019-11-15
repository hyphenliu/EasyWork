from binascii import b2a_hex, a2b_hex
from email.header import Header
from email.utils import parseaddr, formataddr
import re, os, smtplib
from django.conf import settings
from Crypto.Cipher import AES

from EasyWork.utils.database_ops import *


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
    email_pattern = re.compile('^[a-z][-a-z0-9\.]*@[-a-z0-9]+[\.-a-z0-9]*\.(com|cn|net|edu|info)$', re.I)
    mail_address_list = email_str.split(sep)
    for mal in mail_address_list:
        alias, address = parseaddr(mal)
        if not email_pattern.match(address):
            return 'Mail address error'
    return 'Mail address checked'


def checkCipher(cipher):
    '''
    检查加密密码
    :param cipher:
    :return:
    '''
    try:
        decrypt(cipher, open(os.path.join(settings.TEST_DIRS, 'config', 'passwd'), 'rb').read())
        return 'Cipher checked'
    except Exception as e:
        return 'Cipher error'


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
        print('[ERROR][email login] %s' % e)
        return 'Email checked error'


def extractHuwangInfo():
    pass


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
