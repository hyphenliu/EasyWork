#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : YJFD_extract.py
@Author: HP.Liew
@Date  : 2019/10/8 10:27
@Desc  :
'''
import random
from selenium import webdriver
#from django.conf import settings


def getYJFDCookie():
    domain = 'http://192.168.146.25:8080/network/'

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless')
    browser = webdriver.Chrome(executable_path=r'D:\PycharmProjects\sharezone\bin\chromedriver.exe', chrome_options=options)
    #browser = webdriver.Chrome(executable_path=settings.CHROME_DRIVER, chrome_options=options)
    browser.implicitly_wait(20)
    data = {
        'usernameHelp': 'admin',
        'passwordHelp': '',
        'captchaHelp': ''
    }
    browser.get('{}accounts/login'.format(domain))
    source_page = browser.page_source
    print(source_page)
    rand_num = random.random()
    img_url = '{}kaptcha/getCheckCode?t={}'.format(domain, rand_num)
    browser.get(img_url)
    print(browser.page_source)
    browser.close()

print('×'*100)
getYJFDCookie()