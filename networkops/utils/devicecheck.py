from selenium import webdriver
import time, ssl, random, shutil, os, smtplib
import openpyxl
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import parseaddr
from collections import defaultdict
from networkops.utils.views_utils import decrypt, formatEmailAddr

ssl._create_default_https_context = ssl._create_unverified_context


class CheckDevice:
    def initVar(self):
        '''
        初始化时间数值和其他相关参数，只能运行一次初始化一次，不然就会有问题！
        :return:
        '''
        param_dict = defaultdict()
        check_config = os.path.join(settings.TEST_DIRS, 'config', 'devicecheck')
        with open(check_config, 'r') as f:
            flcontent = f.read()
            flcontent = flcontent.split('#')
        for fl in flcontent:
            k, v = fl.split('=')
            param_dict[k] = v
        self.inspector = param_dict['inspector']
        self.checker = param_dict['checker']
        self.recevier = formatEmailAddr(param_dict['recevier'])
        self.cc = formatEmailAddr(param_dict['cc'])
        self.sender = formatEmailAddr(param_dict['sender'])[0]
        self.mail_address = parseaddr(param_dict['sender'])[-1]
        self.smtp_server = 'smtp.chinamobile.com'
        self.password = param_dict['passwd']
        self.bodymessage = param_dict['bodymessage']
        self.passwdFile = os.path.join(settings.TEST_DIRS, 'config', 'passwd')
        self.passwd = decrypt(param_dict['cipher'], open(self.passwdFile, 'rb').read()).split('井')
        #############################################################################
        ct = time.localtime(time.time())
        year, month, day, hour, minute = ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min
        if hour == 0:
            day = day - 1
            hour = 24
        self.hourStr = "%02d点-%02d点" % (hour - 2, hour)  # 06:00-08:00
        self.dateStr1 = '%02d%02d' % (month, day)  # 0615
        self.dateStr2 = '%s年%02d月%02d日' % (year, month, day)  # 2019年06月15日
        self.dateStr3 = '%02d月%02d日%s' % (month, day, self.hourStr)  # 06月15日18:00点
        self.reportFileName = os.path.join(settings.TEST_DIRS, 'doc',
                                           '核心设备每日检查表-深圳-%s(%s).xlsx' % (self.dateStr1, self.hourStr))
        self.reportTempFile = os.path.join(settings.TEST_DIRS, 'doc', '核心设备每日检查表-深圳-模版.xlsx')
        self.zipFile = os.path.join(settings.TEST_DIRS, 'doc', '核心设备每日检查表-深圳%s.zip' % self.dateStr1)
        self.zip_base_name = os.path.split(self.zipFile)[-1]
        if os.path.exists(self.zipFile):
            os.remove(self.zipFile)

    def initBroswer(self):
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

    def check(self):
        '''
        设备巡检
        :return: 返回巡检失败的主机
        '''
        failedList = []
        try:
            self.initBroswer()
        except Exception as e:
            print('[ERROR] Init browser failed.%s' % e)
            self.browser.quit()
            return ['failed', 'failed']

        for host, items in self.data.items():
            for ip in items['ip']:
                print('*' * 79)
                print('[INFO] Start checking [%s] ...' % ip)
                self.browser.get('https://%s' % ip)
                if self.browser.page_source == '<html><head></head><body></body></html>':
                    print('[ERROR] Connect %s failed. Network error.' % ip)
                    failedList.append('Connect %s failed' % ip)
                    continue
                self.browser.find_element_by_id(items['userid']).send_keys(items['user'])
                self.browser.find_element_by_id(items['passwordid']).send_keys(items['password'])
                self.browser.find_element_by_css_selector(items['submit']).click()
                content = str(self.browser.page_source)

                if items['keywords'] in ' '.join(content.split('\n')):
                    print('[INFO] Login %s Success' % ip)
                else:
                    print('[ERROR] Login %s Failed' % ip)
                    failedList.append(ip + ' login failed')

                for url in items['infourl']:
                    print('[INFO] Visiting %s' % url)
                    int = random.randint(10, 15)
                    time.sleep(int)
                    self.browser.get('https://%s/%s' % (ip, url))
                print('[INFO] Logout %s .' % ip)
        print('[INFO] Check complete!')
        self.browser.quit()
        return failedList

    def report(self):
        '''
        生成报告
        :return:返回是否生成报告成功
        '''
        print('[INFO] Product report')
        shutil.copy(self.reportTempFile, self.reportFileName)
        wb = openpyxl.load_workbook(self.reportFileName)
        ws = wb.worksheets[0]
        ws.title = self.dateStr1
        ws["C1"] = "检查时段%s" % self.dateStr3
        for i in range(3, 12):
            ws.cell(i, 5, self.inspector)
            ws.cell(i, 6, self.checker)
        try:
            wb.save(self.reportFileName)
            print('[INFO] Product report %s success!' % self.reportFileName)
            return True
        except Exception as e:
            print('[ERROR] Product report %s failed. %s' % (self.reportFileName, e))
            return False

    def compress(self):
        '''
        加密压缩报告
        :return: 返回是否压缩成功
        '''
        print('[INFO] Compress cipher zip file')
        if settings.op_system == 'Windows':
            compress_cmd = 'Bandizip.exe a -y  -p:%s %s %s' % (self.passwd[3], self.zipFile, self.reportFileName)
        else:
            compress_cmd = 'zip -rP:%s %s %s' % (self.passwd[3], self.zipFile, self.reportFileName)
        time.sleep(random.randint(10, 15))
        try:
            os.system(compress_cmd)
            print('[INFO] Compress zip %s success!' % self.zipFile)
            return True
        except Exception as e:
            print('[ERROR] Compress zip %s encounter en error!' % self.zipFile)
            print(e)
            return False

    def send(self):
        '''
        发送邮件
        :return: 返回是否发送成功
        '''
        print('[INFO] Prepare send email')
        msg_root = MIMEMultipart('related')
        msg_root['subject'] = Header('%s%s深圳侧核心设备巡检' % (self.dateStr2, self.hourStr))
        msg_root['to'] = ','.join(self.recevier)
        msg_root['cc'] = ','.join(self.cc)
        msg_root['from'] = self.sender
        msg_root['date'] = time.ctime()

        body = """各位好，
    %s%s深圳核心设备巡检无异常，检查人：%s、复核人：%s，详见附件%s""" % (
            self.dateStr2, self.hourStr, self.inspector, self.checker, self.bodymessage)
        b_body = MIMEText(body, 'plain', 'utf-8')
        msg_root.attach(b_body)

        part = MIMEApplication(open('%s' % self.zipFile, 'rb').read())
        # 解决outlook显示附件为bin
        part.add_header('Content-Disposition', 'attachment', filename=Header(self.zip_base_name, 'utf-8').encode())
        msg_root.attach(part)

        s_smtp = smtplib.SMTP(self.smtp_server, 25)
        s_smtp.login(self.mail_address, self.password)
        try:
            s_smtp.sendmail(self.sender, self.recevier + self.cc, str(msg_root))
            s_smtp.quit()
            print('[INFO] Email sent!')
            return True
        except Exception as e:
            s_smtp.quit()
            print('[ERROR] Send email encounter en error. %s' % e)
            return False

    def program(self):
        self.initVar()
        time.sleep(random.randint(0, 1) * 60)
        result = self.check()
        if result:  # 巡检失败
            return result
        time.sleep(random.randint(0, 3) * 60)
        if not self.report():  # 生成报告失败
            return 'Gener report failed.'
        time.sleep(random.randint(0, 3) * 60)
        if not self.compress():  # 压缩文件失败
            return 'Compress cipher zip file failed'
        time.sleep(random.randint(0, 3) * 60)
        if not self.send():  # 发送邮件失败
            return 'Send email encounter error'
        return 'success'

    def deviceCheck(self):
        '''
        巡检和
        :return:
        '''
        for i in range(3):
            if not self.program() == 'success':
                time.sleep(1 * 60)
            else:
                break

# oa = CheckDevice()
# oa.check()
