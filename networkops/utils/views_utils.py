import os
from django.conf import settings
from EasyWork.utils.en_decrypt import *


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


def extractHuwangInfo():
    pass


