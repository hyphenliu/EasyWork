# coding=utf-8
from dailywork.models import *

# 数据库表
tableClass = {'contact': Contact, 'sox': SOX}

tableColums = {
    'contact': ['organization', 'department', 'name', 'address', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
    'sox': ['staff', 'stand_point', 'province_point', 'area', 'procedure', 'sub_procedure', 'control_goal',
            'company_describe', 'standard_describe', 'frequency', 'control_type', 'control_method', 'department_list',
            'duty', 'classification', 'reference_file', 'focus_point', 'test_file', 'update'],
}

tableTitles = {
    'contact': ['公司', '部门', '姓名', '办公地点', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
    'sox': ['部门责任人', '标准控制点编号', '公司控制点编号', '适用范围', '业务流程', '子流程', '控制目标', '公司控制点描述', '标准控制点描述', '发生频率', '控制类型', '控制方式',
            '具体部门', '控制点负责人', '控制点分类', '参考文件', '建议关注点', '参考的穿行测试资料', '添加时间'],
}

htmlTitles = {
    'contact': ['部门', '姓名', '办公地点', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
    'sox': ['部门责任人', '标准控制点编号', '公司控制点编号', '控制目标', '公司控制点描述', '发生频率', '控制类型', '具体部门', '控制点负责人', '参考文件',
            '参考的穿行测试资料', '添加时间'],
}

htmlColums = {
    'contact': ['department', 'name', 'address', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
    'sox': ['staff', 'stand_point', 'province_point', 'control_goal', 'company_describe', 'frequency', 'control_type',
            'department_list', 'duty', 'reference_file', 'test_file', 'update'],
}

fileNames = {
    'contact': '联系人列表',
    'taxi': '交通票据',
    'sox': 'SOX内控矩阵',
}
