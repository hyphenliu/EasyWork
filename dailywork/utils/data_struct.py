# coding=utf-8
from dailywork.models import *

# 数据库表
tableClass = {'contact': Contact}

tableColums = {
    'contact': ['organization', 'department', 'name', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
}

tableTitles = {
    'contact': ['公司', '部门', '姓名', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
}

htmlTitles = {
    'contact': ['部门', '姓名', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
}

htmlColums = {
    'contact': ['department', 'name', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
}

fileNames = {
    'contact': '联系人列表',
    'taxi': '交通票据',
}
