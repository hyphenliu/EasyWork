#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : SOX.py
@Author: HP.Liew
@Date  : 2019/8/22 16:36
@Desc  : 
'''
import os
from openpyxl import Workbook, load_workbook
from EasyWork.settings import DOWNLOAD_DIRS
from dailywork.utils.database_ops import *

sox_list = ['stand_point', 'province_point', 'area', 'procedure', 'sub_procedure', 'control_goal',
            'standard_describe', 'company_describe', 'frequency', 'control_type', 'control_method', 'department_list',
            'duty', 'classification', 'reference_file', 'focus_point', 'test_file']
sox_feature = ['标准控制点编号', '控制点编号', '适用范围', '业务流程', '子流程', '控制目标', '标准控制点描述', '控制点描述', '频率', '控制类型', '控制方式',
               '部门', '负责人', '控制点分类', '参考文件', '建议关注点', '穿行测试资料']


def getXlsContent(filename, department='基础平台'):
    '''
    主程序入口
    提取部门控制矩阵
    :param filename:
    :return: {'matrix':{'省控制点编号':{'字段':字段值,...}},'orgin':[[col1,col2,...],...]}
    '''
    ws_result = {}
    ws_ori_result = []  # 保存原始信息
    staff_dict = getContactList(department)
    wb = load_workbook(filename)
    for sn in wb.sheetnames:  # 处理每个sheet

        print('sheet name:{0}'.format(sn))
        ws = wb[sn]
        feature_cols = getHeadLine(ws)
        if not feature_cols: continue
        nrows = ws.max_row  # 最大行数
        ncols = ws.max_column  # 最大列数
        start_row_num = feature_cols['row_num']
        feature_cols.pop('row_num')
        # 保存表头信息
        head_line = [cellValue(c) for c in ws[start_row_num]]
        head_line.insert(1, '部门责任人')
        ws_ori_result.append(head_line)
        # 处理每一行
        for row in range(start_row_num, nrows + 1):
            item = {}
            # 提取部门员工，未含本部门员工则跳过
            staff_cell = ws.cell(row=row, column=feature_cols['duty']).value
            if not staff_cell: continue
            staff_list = extractContactor(staff_cell, staff_dict)
            if not staff_list: continue

            department_cell = ws.cell(row=row, column=feature_cols['department_list']).value
            # 提取可能存在问题的信息
            if not departmentFilter(department_cell, staff_cell): staff_list = '[注意]' + staff_list
            for k, v in feature_cols.items():
                if v < 0:
                    item[k] = '未提取到'
                    continue
                item[k] = cellValue(ws.cell(row=row, column=v))
            item['duty'] = staff_cell
            item['staff'] = staff_list
            if not item['province_point'] in ws_result:  # 不重复控制点
                # 提取本门控制点原始信息
                o_list = [cellValue(c) for c in ws[row]]
                o_list.insert(1, staff_list)  # 插入部门联系人信息
                ws_ori_result.append(o_list)
                ws_result[item['province_point']] = item
    writeContent(filename, ws_ori_result)
    return ws_result


def cellValue(cell):
    if not cell.value:
        return ' '
    if isinstance(cell.value, str):
        return cell.value.replace('\n', '')
    return cell.value


def getHeadLine(sheet_content):
    '''
    返回字段所在的行/列号，没有找到的字段列号为-1
    :param sheet_content:
    :return: result{sox_list:column_num}
    '''
    result = {}
    col_num = []
    department_flag = False  # 区分“具体部门”和“部门”
    for sl in sox_list:
        result[sl] = -1
    row_num = -1
    # 找到首行
    for row in sheet_content.rows:
        count = 0
        cell_values = '|'.join([cellValue(c) for c in row])
        cell_values = cell_values.replace('\n', '').strip('|')
        for sf in sox_feature:
            if sf in cell_values: count += 1
        if count > len(sox_feature) / 2:
            row_num = row[1].row
            if '具体部门' in cell_values: department_flag = True
            break
    if row_num < 0:
        print('【ERROR】解析Excel出错，没有找到超过半数的特征值行')
        return
    # 找到字段对应的列
    result['row_num'] = row_num
    for cell in sheet_content[row_num]:
        cv = cell.value
        if not isinstance(cv, str) or not cv:
            # print('【ERROR】解析Excel第{0}行出错，存在单元格为空'.format(row_num))
            continue
        for sf in sox_feature:
            key = sox_list[sox_feature.index(sf)]
            if sf == '部门' and department_flag: sf = '具体部门'
            if sf in cv and (result[key] < 0) and (cell.column not in col_num):
                result[key] = cell.column
                col_num.append(cell.column)
    return result


def extractContactor(xls_data, staff_dict):
    '''
    提取出部门控制点责任人
    :param xls_data:
    :param staff_list:
    :return: '责任人1,责任人2,...
    '''
    result = []
    phone_flag = False
    pattern = re.compile('[^\u4e00-\u9fa5]')
    data = pattern.split(xls_data)  # 提取责任人名字
    if re.findall(r'\d{11}', xls_data): phone_flag = True  # 是否包含手机号码
    for k, v in staff_dict.items():
        k = pattern.split(k)[0]
        if k in data:
            if phone_flag and not v in xls_data:
                continue
            result.append(k)

    return ','.join(result)


def departmentFilter(dep_data, staff_cell):
    for i in ['基础', '实物管理部门', '工程建设部门', '各采购需求部门', '各采购验收部门', '工程实施部门']:
        if i in dep_data:
            return True
    if '基础' in staff_cell:
        return True


def getContactList(department):
    '''
    根据部门查询部门员工姓名和电话
    :param department:
    :return: {'姓名':电话,...}
    '''
    result = {}
    datas = getSingleData('contact', 'department', department).values()
    for data in datas:
        result[data['name']] = data['phone']
    return result


def writeContent(filename, data):
    filename, ext = os.path.splitext(filename)

    print(filename)
    pass
