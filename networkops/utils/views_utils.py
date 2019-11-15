from binascii import b2a_hex, a2b_hex
from email.header import Header
from email.utils import parseaddr, formataddr
import re, os, smtplib
from django.conf import settings
from Crypto.Cipher import AES

from networkops.utils.database_ops import *


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


def simpleQuery(request, tablename, prefix=''):
    columnNames = []
    columnValues = []
    simpleValue = []

    if request.method == 'GET':
        columnname1 = request.GET.get('%scolumnname1' % prefix, '').strip()
        columnname2 = request.GET.get('%scolumnname2' % prefix, '').strip()
        columnvalue1 = request.GET.get('%scolumnvalue1' % prefix, '').strip()
        columnvalue2 = request.GET.get('%scolumnvalue2' % prefix, '').strip()

        if columnname1 and columnvalue1:
            columnNames.append(columnname1)
            columnValues.append(columnvalue1)
        elif columnvalue1 and not columnname1:
            simpleValue.append(columnvalue1)
        if columnname2 and columnvalue2:
            columnNames.append(columnname2)
            columnValues.append(columnvalue2)
        elif columnvalue2 and not columnname2:
            simpleValue.append(columnvalue2)

    if len(columnNames) == 1:
        dataList = getSingleData(tableName=tablename, columnName=columnNames[0], columnValue=columnValues[0]).values()
    elif len(columnNames) == 2:
        dataList = getDoubleData(tableName=tablename, columnNames=columnNames, columnValues=columnValues).values()
    elif len(simpleValue) == 1:
        dataList = getReSingleData(tableName=tablename, value= simpleValue[0]).values()
    else:
        dataList = getAll(tablename).values()
    return dataList, '-'.join(columnValues)


# def export2Xls(data, tablename):
#     result = []
#     columns = htmlColums[tablename]
#     for dt in data:
#         line = []
#         for i in columns:
#             line.append(dt[i])
#         result.append(line)
#     return result


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
