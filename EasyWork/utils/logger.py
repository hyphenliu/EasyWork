#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : logger.py.py
@Author: HP.Liew
@Date  : 2019/8/1 15:48
@Desc  : 
'''
import logging.config
logging.config.fileConfig("./conf/logger.ini")
logger = logging.getLogger("easywork")

if __name__=='__main__':
    logger.info(msg="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    logger.error(
        msg="eyJ1c2VybmFtZSI6IndlbGxpYW0iLCJ1c2VyX2lkIjoyLCJlbWFpbCI6IjMwMzM1MDAxOUBxcS5jb20iLCJleHAiOjE1MTk2NTUzNTB9")