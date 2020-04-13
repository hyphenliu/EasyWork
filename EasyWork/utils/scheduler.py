#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : scheduler.py
@Author: HP.Liew
@Date  : 2020/2/18 17:03
@Desc  : 计划任务调度
### wsig.py ###
# import os
# from django.core.wsgi import get_wsgi_application
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_apscheduler.settings")
# application = get_wsgi_application()
### register_job 参数 ###
# scheduler, trigger=None, args=None, kwargs=None, id=None, name=None,
# misfire_grace_time=undefined, # 容错时间，单位为秒
# coalesce=undefined, # True 或 False 错过执行时间，只执行一次或执行错过的所有次数
# max_instances=undefined,
# next_run_time=undefined, jobstore='default', executor='default',
# replace_existing=False, **trigger_args
'''
import random, time,logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from networkops.utils.devicecheck import CheckDevice
from networkops.utils.feixin_extract import updateDatabase
from dailywork.utils.sox_remainder import soxReminder
from dailywork.utils.contact_information import OA

sched = BackgroundScheduler()
sched.add_jobstore(DjangoJobStore(), 'default')


try:
    logger = logging.getLogger('default')
    # logger.info('开始执行定时任务')

    # @register_job(sched, trigger='interval', seconds=10, start_date='2019-09-19 00:00:20',
    #               end_date='2019-10-10 00:00:03', id='extractfeixin')
    # def extractFeixin():
    #     updateDatabase()
    #
    #
    # @register_job(sched, trigger='interval', hours=2, start_date='2020-02-16 00:00:00', end_date='2020-02-21 10:00:00',
    #               id='checkdevice', misfire_grace_time=60*60, coalesce=Ture)
    # def sendMail():
    #     cd = CheckDevice()
    #     cd.deviceCheck()

    @register_job(scheduler=sched, trigger='cron', day_of_week='mon-fri', hour='10', minute='30', second='10',id='sox_time', coalesce=True)
    def remindExcuteSOX():
        logger.info('执行SOX提醒任务')
        soxReminder()


    register_events(sched)  # 监控服务
    sched.start()
except Exception as e:
    print('[ERROR] Excute schedual error. %s' % e)
    sched.shutdown()
