#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : phone.py
@Author: HP.Liew
@Date  : 2019/8/26 11:04
@Desc  : 本程序不用更改，只需要每次更新指定目录下的“phone.dat”文件即可
'''
import os
import struct
import sys
import urllib.request
import ssl
from EasyWork.settings import TEST_DATA_DIR

if sys.version_info > (3, 0):
    def get_record_content(buf, start_offset):
        end_offset = buf.find(b'\x00', start_offset)
        return buf[start_offset:end_offset].decode()
else:
    def get_record_content(buf, start_offset):
        end_offset = buf.find('\x00', start_offset)
        return buf[start_offset:end_offset]


class Phone(object):
    def __init__(self, dat_file=None):

        if dat_file is None:
            # https://github.com/xluohome/phonedata/blob/master/phone.dat
            dat_file = os.path.join(TEST_DATA_DIR, "phone.dat")

        with open(dat_file, 'rb') as f:
            self.buf = f.read()

        self.head_fmt = "<4si"
        self.phone_fmt = "<iiB"
        self.head_fmt_length = struct.calcsize(self.head_fmt)
        self.phone_fmt_length = struct.calcsize(self.phone_fmt)
        self.version, self.first_phone_record_offset = struct.unpack(
            self.head_fmt, self.buf[:self.head_fmt_length])
        self.phone_record_count = (len(
            self.buf) - self.first_phone_record_offset) // self.phone_fmt_length

    def get_phone_dat_msg(self):
        print("版本号:{}".format(self.version))
        print("总记录条数:{}".format(self.phone_record_count))

    @staticmethod
    def get_phone_no_type(no):
        if no == 4:
            return "电信虚拟运营商"
        if no == 5:
            return "联通虚拟运营商"
        if no == 6:
            return "移动虚拟运营商"
        if no == 3:
            return "电信"
        if no == 2:
            return "联通"
        if no == 1:
            return "移动"

    @staticmethod
    def _format_phone_content(phone_num, record_content, phone_type):

        province, city, zip_code, area_code = record_content.split('|')
        return {
            "phone": phone_num,
            "province": province,
            "city": city,
            "zip_code": zip_code,
            "area_code": area_code,
            "phone_type": Phone.get_phone_no_type(phone_type)
        }

    def _lookup_phone(self, phone_num):

        phone_num = str(phone_num)
        assert 7 <= len(phone_num) <= 11
        int_phone = int(str(phone_num)[0:7])

        left = 0
        right = self.phone_record_count
        buflen = len(self.buf)
        while left <= right:
            middle = (left + right) // 2
            current_offset = (self.first_phone_record_offset +
                              middle * self.phone_fmt_length)
            if current_offset >= buflen:
                return

            buffer = self.buf[current_offset: current_offset + self.phone_fmt_length]
            cur_phone, record_offset, phone_type = struct.unpack(self.phone_fmt,
                                                                 buffer)

            if cur_phone > int_phone:
                right = middle - 1
            elif cur_phone < int_phone:
                left = middle + 1
            else:
                record_content = get_record_content(self.buf, record_offset)
                return Phone._format_phone_content(phone_num, record_content,
                                                   phone_type)

    def find(self, phone_num):
        return self._lookup_phone(phone_num)

    @staticmethod
    def human_phone_info(phone_info):
        if not phone_info:
            return ''

        return "{}|{}{}|{}".format(phone_info['phone'],
                                   phone_info['province'],
                                   phone_info['city'],
                                   phone_info['phone_type'])

    def getPhoneLocation(self, phone_number):
        '''
        本地查询不到的归属地使用在线API查询
        :param phone_number:
        :return:
        '''
        url = 'https://jshmgsdmfb.market.alicloudapi.com/shouji/query?shouji={0}'.format(phone_number)
        appcode = 'bfaaf6ee343343ad8d22c0703a3060f2'

        request = urllib.request.Request(url)
        request.add_header('Authorization', 'APPCODE ' + appcode)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        response = urllib.request.urlopen(request, context=ctx)
        content = response.read()
        if (content):
            content = eval(content)
            lc = content.get('result')
            return "{}|{}{}|{}".format(phone_number,
                                       lc['province'],
                                       lc['city'],
                                       lc['cardtype'])

    def main(self, phone_number):
        '''
        根据输入的手机号码返回本地数据库中的归属地
        :param phone_number:
        :return:
        '''
        if len(phone_number) < 7:
            return
        if not len(phone_number) == 11:
            phone_number = phone_number + '1' * (11 - len(phone_number))
        result = self.human_phone_info(self.find(phone_number))
        if not result:
            result = self.getPhoneLocation(phone_number)
        return result
