# -*- coding: utf-8 -*-
import os
import configparser
from django.conf import settings


class Config(object):
    '''
    读取给定的配置文件内容，并根据需要返回键值对
    '''

    def __init__(self, config_file='config.ini'):
        self._path = os.path.join(settings.CONF_DIR, config_file)
        if not os.path.exists(self._path):
            raise FileNotFoundError(f"没有找到配置文件:{config_file}")

        self._config = configparser.ConfigParser()
        self._config.read(self._path, encoding='utf-8')
        self._configRaw = configparser.RawConfigParser()
        self._configRaw.read(self._path, encoding='utf-8')

    def setRaw(self, section, option, value):
        self._configRaw.set(section, option, value)

    def set(self, section, option, value):
        self._config.set(section, option, value)

    def get(self, section, name):
        return self._config.get(section, name)

    def getRaw(self, section, name):
        return self._configRaw.get(section, name)

    def writeRaw(self):
        with open(self._path, 'w', encoding='utf-8') as f:
            self._configRaw.write(f)
