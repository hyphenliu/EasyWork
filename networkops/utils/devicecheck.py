#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : mail_sender.py
@Author: HP.Liew
@Date  : 2019/5/7 10:29
@Desc  :
'''
import ssl
import random
import shutil
import openpyxl
from selenium import webdriver
from django.conf import settings
from collections import defaultdict
from EasyWork.utils.en_decrypt import decrypt
from EasyWork.utils.mail_utils import *

ssl._create_default_https_context = ssl._create_unverified_context


class CheckDevice:
    def _initVar(self):
        '''
        初始化时间数值和其他相关参数，只能运行一次初始化一次，不然就会有问题！
        :return:
        '''
        param_dict = defaultdict()
        check_config = os.path.join(settings.CONF_DIR, 'devicecheck')
        with open(check_config, 'r') as f:
            flcontent = f.read()
            flcontent = flcontent.split('#')
        for fl in flcontent:
            k, v = fl.split('=')
            param_dict[k] = v
        self.inspector = param_dict['inspector']
        self.checker = param_dict['checker']
        self.recevier = param_dict['recevier']
        self.cc = param_dict['cc']
        self.sender = param_dict['sender']
        self.mail_address = parseaddr(param_dict['sender'])[-1]
        self.smtp_server = 'smtp.chinamobile.com'
        self.password = param_dict['passwd']
        self.mailsign = param_dict['mailsign']
        self.passwdFile = os.path.join(settings.TEST_DIRS, 'config', 'passwd')
        self.passwd = decrypt(param_dict['cipher'], open(self.passwdFile, 'rb').read()).split('井')
        #############################################################################
        ct = time.localtime(time.time())
        year, month, day, hour, minute = ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min
        if hour == 0:
            day = day - 1
            hour = 24
        self.hourStr = "{:0>2d}点-{:0>2d}点".format(hour - 2, hour)  # 06:00-08:00
        self.dateStr1 = '{:0>2d}{:0>2d}'.format(month, day)  # 0615
        self.dateStr2 = '{}年{:0>2d}月{:0>2d}日'.format(year, month, day)  # 2019年06月15日
        self.dateStr3 = '{:0>2d}月{:0>2d}日{}'.format(month, day, self.hourStr)  # 06月15日18:00点
        self.reportFileName = os.path.join(settings.TEST_DIRS, 'doc',
                                           '核心设备每日检查表-深圳{}({}).xlsx'.format(self.dateStr1, self.hourStr))
        self.reportTempFile = os.path.join(settings.TEST_DIRS, 'doc', '核心设备每日检查表-深圳-模版.xlsx')
        self.zip_file = os.path.join(settings.TEST_DIRS, 'doc', '核心设备每日检查表-深圳{}.zip'.format(self.dateStr1))
        self.zip_base_name = os.path.split(self.zip_file)[-1]
        if os.path.exists(self.zip_file):
            os.remove(self.zip_file)

    def _initBroswer(self):
        '''
        初始化无头浏览器
        :return:
        '''
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER, chrome_options=options)
        self.browser.implicitly_wait(20)
        self.data = {
            'pa': {'ip': ['192.168.99.245', '192.168.99.246'], 'keywords': 'predefined-top-attackers-table',
                   'userid': 'user', 'user': 'admin1',
                   'passwordid': 'passwd', 'password': self.passwd[0], 'submit': "input[type='submit'][name='ok']",
                   'infourl': ['#dashboard::', 'php/logout.php']},
            'f5': {'ip': ['192.168.99.71', '192.168.99.81'], 'keywords': 'Current Redundancy State',
                   'userid': 'username', 'user': 'admin',
                   'passwordid': 'passwd', 'password': self.passwd[1], 'submit': "button[type='submit']",
                   'infourl': ['xui', 'dms/logout.php']},
            'sw': {'ip': ['192.168.33.58', ], 'keywords': '网络设备及服务器', 'userid': 'ctl00_BodyContent_Username',
                   'user': 'admin',
                   'passwordid': 'ctl00_BodyContent_Password', 'password': self.passwd[2],
                   'submit': "span[class='sw-btn-t']",
                   'infourl': ['/Orion/SummaryView.aspx?viewname=Current%20Top%2010%20Lists', 'Orion/Logout.aspx']}
        }

    def _check(self):
        '''
        设备巡检
        :return: 返回巡检失败的主机
        '''
        failedList = []
        try:
            self._initBroswer()
        except Exception as e:
            print('[ERROR] Init browser failed.{}'.format(e))
            self.browser.quit()
            return ['failed', 'failed']

        for host, items in self.data.items():
            for ip in items['ip']:
                print('*' * 79)
                print('[INFO] Start checking [{}] ...'.format(ip))
                self.browser.get('https://{}'.format(ip))
                if self.browser.page_source == '<html><head></head><body></body></html>':
                    print('[ERROR] Connect {} failed. Network error.'.format(ip))
                    failedList.append('Connect {} failed'.format(ip))
                    continue
                self.browser.find_element_by_id(items['userid']).send_keys(items['user'])
                self.browser.find_element_by_id(items['passwordid']).send_keys(items['password'])
                self.browser.find_element_by_css_selector(items['submit']).click()
                content = str(self.browser.page_source)

                if items['keywords'] in ' '.join(content.split('\n')):
                    print('[INFO] Login {} Success'.format(ip))
                else:
                    print('[ERROR] Login {} Failed'.format(ip))
                    failedList.append(ip + ' login failed')

                for url in items['infourl']:
                    print('[INFO] Visiting {}'.format(url))
                    int = random.randint(10, 15)
                    time.sleep(int)
                    self.browser.get('https://{}/{}'.format(ip, url))
                print('[INFO] Logout {} .'.format(ip))
        print('[INFO] Check complete!')
        self.browser.quit()
        return failedList

    def _report(self):
        '''
        生成报告
        :return:返回是否生成报告成功
        '''
        print('[INFO] Product report')
        shutil.copy(self.reportTempFile, self.reportFileName)
        wb = openpyxl.load_workbook(self.reportFileName)
        ws = wb.worksheets[0]
        ws.title = self.dateStr1
        ws["C1"] = "检查时段{}".format(self.dateStr3)
        for i in range(3, 12):
            ws.cell(i, 5, self.inspector)
            ws.cell(i, 6, self.checker)
        try:
            wb.save(self.reportFileName)
            print('[INFO] Product report {} success!'.format(self.reportFileName))
            return True
        except Exception as e:
            print('[ERROR] Product report {} failed. {}'.format(self.reportFileName, e))
            return False

    def _compress(self):
        '''
        加密压缩报告
        :return: 返回是否压缩成功
        '''
        print('[INFO] Compress cipher zip file')
        if settings.op_system == 'Windows':
            compress_cmd = 'Bandizip.exe a -y  -p:{} {} {}'.format(self.passwd[3], self.zip_file, self.reportFileName)
        else:
            compress_cmd = 'zip -rP:{} {} {}'.format(self.passwd[3], self.zip_file, self.reportFileName)
        time.sleep(random.randint(10, 15))
        try:
            os.system(compress_cmd)
            print('[INFO] Compress zip {} success!'.format(self.zip_file))
            return True
        except Exception as e:
            print('[ERROR] Compress zip {} encounter en error!'.format(self.zip_file))
            print(e)
            return False

    def _send(self):
        '''
        发送邮件
        :return: 返回是否发送成功
        '''
        print('[INFO] Prepare send email')
        title = '{}{}深圳侧核心设备巡检'.format(self.dateStr2, self.hourStr)
        body = """各位好，
            {}{}深圳核心设备巡检无异常，检查人：{}、复核人：{}，详见附件{}""".format(
            self.dateStr2, self.hourStr, self.inspector, self.checker, self.mailsign)
        return mailSender(title=title, sender=self.sender, recevier=self.recevier, cc=self.cc, body=body,
                          sender_mail=self.mail_address, sender_pass=self.passwd, file_name=self.zip_file)

    def _program(self):
        self._initVar()
        time.sleep(random.randint(0, 1) * 60)
        result = self._check()
        if result:  # 巡检失败
            return result
        time.sleep(random.randint(0, 3) * 60)
        if not self._report():  # 生成报告失败
            return 'Gener report failed.'
        time.sleep(random.randint(0, 3) * 60)
        if not self._compress():  # 压缩文件失败
            return 'Compress cipher zip file failed'
        time.sleep(random.randint(0, 3) * 60)
        if not self._send():  # 发送邮件失败
            return 'Send email encounter error'
        return 'success'

    def deviceCheck(self):
        '''
        巡检和
        :return:
        '''
        for i in range(3):
            if not self._program() == 'success':
                time.sleep(1 * 60)
            else:
                break

# oa = CheckDevice()
# oa.check()
