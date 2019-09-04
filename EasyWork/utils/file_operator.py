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
from datetime import datetime, date

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
from networkops.utils import database_ops as network_dbops
from dailywork.utils import SOX
from networkops.utils import accesslist

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
        fileData = SOX.getXlsContent(tableName, filePath, department='基础平台')
        return daily_dbops.importDatabase(tableName, fileData)


def dealNetworkImportFile(filePath, tableName, fileName):
    '''
    导入网络管理数据
    :param filePath:
    :param tableName:
    :param fileName:
    :return:
    '''
    # 导入网络策略开通表
    if tableName == 'accesslist':
        fileData, msg = accesslist.readXlsContent(tableName, filePath)
        cache.set('pageShowOn{}'.format(tableName), msg, 5 * 60)
        return network_dbops.importDatabase(tableName, fileData, dropTable=True)


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


def dealDailyworkQueryFile(filePath, tableName, htmlColums):
    '''
    处理日常工作批量查询文件
    :param filePath:
    :param tableName:
    :param htmlColums:
    :return:
    '''


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
        elif module == 'network':
            return dealNetworkImportFile(filePath, tableName, fileName)

    elif action == 'query':
        result = []
        if module == 'assets':
            result = dealErpQueryFile(filePath, tableName, htmlColums)
        if module == 'dailywork':
            result = dealDailyworkQueryFile(filePath, tableName, htmlColums)
        cache.set('exportQuery{}2XlsContent'.format(tableName), result, 2 * 60)
        cache.set('exportQuery{}2XlsName'.format(tableName), tableName, 2 * 60)
        cache.set('batchQuery{}Status'.format(tableName), 'success', 60)
        return True


def responseXls(module, tableName, data, dataName):
    '''

    :param module:
    :param tableName:
    :param data:
    :param dataName:
    :return:
    aqua 0x31; black 0x08; blue 0x0C; blue_gray 0x36; bright_green 0x0B; brown 0x3C; coral 0x1D; cyan_ega 0x0F;
    dark_blue 0x12; dark_blue_ega 0x12; dark_green 0x3A; dark_green_ega 0x11; dark_purple 0x1C; dark_red 0x10;
    dark_red_ega 0x10; dark_teal 0x38; dark_yellow 0x13; gold 0x33; gray_ega 0x17; gray25 0x16; gray40 0x37;
    gray50 0x17; gray80 0x3F; green 0x11; ice_blue 0x1F; indigo 0x3E; ivory 0x1A; lavender 0x2E; light_blue 0x30;
    light_green 0x2A; light_orange 0x34; light_turquoise 0x29; light_yellow 0x2B; lime 0x32; magenta_ega 0x0E;
    ocean_blue 0x1E; olive_ega 0x13; olive_green 0x3B; orange 0x35; pale_blue 0x2C; periwinkle 0x18; pink 0x0E;
    plum 0x3D; purple_ega 0x14; red 0x0A; rose 0x2D; sea_green 0x39; silver_ega 0x16; sky_blue 0x28; tan 0x2F;
    teal 0x15; teal_ega 0x15; turquoise 0x0F; violet 0x14; white 0x09; yellow 0x0D
    '''
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(dataName)
    htmlTitles = MODULE_DICT[module]['html_titles']
    titles = htmlTitles[tableName]
    style_date = xlwt.XFStyle()
    style_date.num_format_str = 'yyyy-mm-dd'
    style_line = xlwt.XFStyle()
    style_line.alignment.wrap = 1  # 自动换行
    style_line.alignment.vert = 1  # 垂直居中

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
    # 确定栏位宽度
    col_width = []
    for i in range(len(titles)):
        sheet.write(0, i, titles[i], style_heading)
        col_width.append(len_byte(titles[i]))

    for r in range(len(data)):
        for c in range(len(data[r])):
            if col_width[c] / 2 < len_byte(str(data[r][c])):
                col_width[c] = int((len_byte(data[r][c]) + r * col_width[c]) / (r + 1))
            if isinstance(data[r][c], date):
                sheet.write(r + 1, c, data[r][c], style_date)
            else:
                sheet.write(r + 1, c, data[r][c], style_line)
    # 设置栏位宽度，栏位宽度小于10时候采用默认宽度
    for i in range(len(col_width)):
        col_width[i] = int(col_width[i] * 1.2)
        if col_width[i] >= 1 and col_width[i] < 30:
            sheet.col(i).width = 256 * (col_width[i] + 1)
        elif col_width[i] >= 30 and col_width[i] < 80:
            sheet.col(i).width = 256 * (int((col_width[i] - 30) / 3) + 31)
        elif col_width[i] >= 80 and col_width[i] < 180:
            sheet.col(i).width = 256 * (int((col_width[i] - 80) / 5) + 48)
        elif col_width[i] >= 180 and col_width[i] <= 320:
            sheet.col(i).width = 256 * (int((col_width[i] - 30) / 7) + 68)
        elif col_width[i] > 320:
            sheet.col(i).width = 256 * 90

    output = BytesIO()
    wb.save(output)
    return output


def len_byte(value):
    # 获取字符串长度，一个中文的长度为2
    value = str(value)
    length = max(len(i) for i in value.split('\n'))
    utf8_length = max(len(i.encode('utf-8')) for i in value.split('\n'))
    length = int((utf8_length - length) / 2 + length)
    return length


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
