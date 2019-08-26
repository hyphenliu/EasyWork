#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : kconfigparser.py
@Author: HP.Liew
@Date  : 2019/8/6 10:05
@Desc  : 将存入数据库中的inventory host取出来后生成host文件。
         为了解决ConfigParser的冒号/空格等被自动保存为等号而引起的后续解析问题
         重写configpaser中的RawConfigParser类
'''
import json
import configparser


class KconfigParser(configparser.RawConfigParser):
    def write(self, fp):
        """解决ConfigParser的冒号/空格等被自动保存为等号而引起的后续解析问题"""
        if self._defaults:
            fp.write(bytes("[%s]\n" % DEFAULTSECT, encoding='utf8'))
            for (key, value) in self._defaults.items():
                fp.write(bytes("%s  %s\n" % (key, str(value).replace("\n", "\n\t")), encoding='utf8'))
            fp.write(b"\n")
        for section in self._sections:
            fp.write(bytes("[%s]\n" % section, encoding="utf8"))
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write(bytes("%s  %s\n" % (key, str(value).replace("\n", "\n\t")), encoding="utf8"))
            fp.write(b"\n")


class GenerateAnsibleHosts(object):
    def __init__(self, host_file):
        self.config = KconfigParser(allow_no_value=True)
        self.host_file = host_file

    def create_all_servers(self, items):
        for i in items:
            group = i['group']
            self.config.add_section(group)
            for j in i['items']:
                name = j['name']
                ssh_port = j['ssh_port']
                ssh_host = j['ssh_host']
                ssh_user = j['ssh_user']
                build = "ansible_ssh_port={0} ansible_ssh_host={1} ansible_ssh_user={2}".format(ssh_port, ssh_host,
                                                                                                ssh_user)
                self.config.set(group, name, build)
        with open(self.host_file, 'wb') as configfile:
            self.config.write(configfile)
        return True
