#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : file_operator.py
@Author: HP.Liew
@Date  : 2019/8/1 15:52
@Desc  : 
'''
from django.core.cache import cache
from io import BytesIO
import os, xlwt
from datetime import datetime

from inventory.utils.data_struct import tableClass as InventModelClass
from inventory.utils.data_struct import htmlTitles as InventHmtlTitles
from inventory.utils.data_struct import htmlColums as InventHtmlColumns
from inventory.utils.data_struct import tableTitles as InventTableTitles
from inventory.utils.data_struct import tableColums as InventTableColumns
from networkops.utils.data_struct import tableClass as NetworkModelClass
from networkops.utils.data_struct import htmlTitles as NetworkHtmlTitles
from networkops.utils.data_struct import htmlColums as NetworkHtmlColumns
from networkops.utils.data_struct import tableTitles as NetworkTableTitles
from networkops.utils.data_struct import tableColums as NetworkTableColumns
from dailywork.utils.data_struct import tableClass as DailyworkModelClass
from dailywork.utils.data_struct import htmlTitles as DailyworkHtmlTitles
from dailywork.utils.data_struct import htmlColums as DailyworkHtmlColumns
from dailywork.utils.data_struct import tableTitles as DailyworkTableTitles
from dailywork.utils.data_struct import tableColums as DailyworkTableColumns

from inventory.utils import database_ops as asset_dbops
from dailywork.utils import database_ops as daily_dbops
from dailywork.utils import SOX

MODULE_DICT = {
    'assets': {'model_class': InventModelClass, 'html_titles': InventHmtlTitles, 'html_columns': InventHtmlColumns,
               'table_titles': InventTableTitles, 'table_columns': InventTableColumns},
    'network': {'model_class': NetworkModelClass, 'html_titles': NetworkHtmlTitles, 'html_columns': NetworkHtmlColumns,
                'table_titles': NetworkTableTitles, 'table_columns': NetworkTableColumns},
    'dailywork': {'model_class': DailyworkModelClass, 'html_titles': DailyworkHtmlTitles,
                  'html_columns': DailyworkHtmlColumns,
                  'table_titles': DailyworkTableTitles, 'table_columns': DailyworkTableColumns}
}


def readFile(filename, chunkSize=512):
    '''使用缓冲流下载文件方法'''
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunkSize)
            if c:
                yield c
            else:
                break


def dealErpImportFile(filePath, tableName, fileName, tableTitles):
    '''
    处理ERP导入的数据
    :param filePath:
    :param tableName:
    :param fileName:
    :return:
    '''
    if tableName == 'erpsoft':
        tableName = 'erp'
        dropTable = False
    try:
        titleList = tableTitles[tableName]
    except:
        return
    if tableName == 'inventoried':
        titleList = tableTitles['inventory']
    fileData = asset_dbops.readXlsContent(filePath, titleList, fileName)
    os.remove(filePath)
    if not fileData:
        print('没有读取到excel表格数据，请确认是按照模版填写数据')
        return
    if tableName == 'erp' or tableName == 'erpsoft':
        fileData = asset_dbops.completeErpInformation(fileData)
    elif tableName == 'inventoried':
        fileData = asset_dbops.complteInventoriedInformation(fileData)
    elif tableName == 'schedual':
        fileData = asset_dbops.comleteSchedualInformation(fileData)
    return asset_dbops.importDatabase(tableName, fileData, dropTable=dropTable)


def dealDailyworkImportFile(filePath, tableName, fileName):
    '''
    处理导入的日常工作数据，联系人/SOX矩阵
    :param filePath:
    :param tableName:
    :param fileName:
    :return:
    '''
    if tableName == 'sox':
        # {'origin':[[],...],'matrix':{{},...}}
        fileData = SOX.getXlsContent(filePath, department='基础平台')
        return daily_dbops.importDatabase(tableName, fileData)


def dealErpQueryFile(filePath, tableName, htmlColums):
    '''
    处理ERP批量查询文件
    :param filePath:
    :param tableName:
    :param fileName:
    :param htmlColums:
    :return:
    '''
    result = []
    queryList = asset_dbops.readXlsQueryContent(filePath)
    if not queryList:
        print('没有读取到excel表格数据，请确认是按照模版填写数据')
        cache.set('batchQueryStatus', '', 60)
        return False
    columns = htmlColums[tableName]
    for ql in queryList:  # 逐条查询
        items = asset_dbops.getSingleData(tableName, 'asset_label', ql)
        if items:
            for item in items.values():
                line = []
                for i in columns:
                    line.append(item[i])
                line[0] = ql
                result.append(line)
        else:
            line = [' ' for i in range(len(columns) - 1)]
            line.insert(0, ql)
            result.append(line)
    return result


def dealUploadFile(module, filePath, tableName, action, fileName):
    '''
    处理上传文件，根据文件action类型确定是否进行入库操作，或进行查询操作
    :param filePath:临时文件名
    :param tableName:数据表名
    :param action:上传入库为import，上传查询为query
    :param fileName:文件名
    :return:
    '''
    dropTable = True
    tableTitles = MODULE_DICT[module]['table_titles']
    htmlColums = MODULE_DICT[module]['html_columns']
    if action == 'import':
        if module == 'assets':
            return dealErpImportFile(filePath, tableName, fileName, tableTitles)
        elif module == 'dailywork':
            return dealDailyworkImportFile(filePath, tableName, fileName)

    elif action == 'query':
        result = []
        if module == 'assets':
            result = dealErpQueryFile(filePath, tableName, fileName, htmlColums)

        cache.set('exportQuery{}2XlsContent'.format(tableName), result, 2 * 60)
        cache.set('exportQuery{}2XlsName'.format(tableName), tableName, 2 * 60)
        cache.set('batchQuery{}Status'.format(tableName), 'success', 60)
        return True


def responseXls(module, tableName, data, dataName):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(dataName)
    htmlTitles = MODULE_DICT[module]['html_titles']
    titles = htmlTitles[tableName]
    style_date = xlwt.XFStyle()
    style_date.num_format_str = 'yyyy-mm-dd'
    style_heading = xlwt.easyxf("""
                    font:
                        name SimSun,
                        colour_index white,
                        bold on,
                        height 250;
                    align:
                        wrap off,
                        vert center,
                        horiz center;
                    pattern:
                        pattern solid,
                        fore_colour 0x04;
                    borders:
                        left THIN,
                        right THIN,
                        top THIN,
                        bottom THIN;
                    """)
    for i in range(len(titles)):
        sheet.write(0, i, titles[i], style_heading)
    for r in range(len(data)):
        for c in range(len(data[r])):
            if isinstance(data[r][c], datetime.date):
                sheet.write(r + 1, c, data[r][c], style_date)
            else:
                sheet.write(r + 1, c, data[r][c])
    output = BytesIO()
    wb.save(output)
    return output


def export2Xls(module, data, tablename, db=True):
    result = []
    if db:
        columns = MODULE_DICT[module]['html_columns'][tablename]
        for dt in data:
            line = []
            for i in columns:
                line.append(dt[i])
            result.append(line)
    else:
        pass
    return result
