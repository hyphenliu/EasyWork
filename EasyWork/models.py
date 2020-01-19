#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : models.py
@Author: HP.Liew
@Date  : 2020/1/14 14:58
@Desc  : 
'''
from django.db import models

class SoxTasks(models.Model):
    point = models.CharField(max_length=20, verbose_name='控制点编号')
    describe = models.TextField(verbose_name='控制点描述')
    frequency = models.CharField(max_length=20, verbose_name='控制点频率')
    test_file = models.CharField(max_length=250, verbose_name='关注点')
    focus = models.CharField(max_length=250, verbose_name='测试材料')
    exec_date = models.DateField(verbose_name='执行日期')
    next_exec_date = models.DateField(verbose_name='下次执行日期')
    staff = models.CharField(max_length=20, verbose_name='负责人')

class ContactTasks(models.Model):
    exec_date = models.DateField(verbose_name='执行日期')
    next_exec_date = models.DateField(verbose_name='下次执行日期')