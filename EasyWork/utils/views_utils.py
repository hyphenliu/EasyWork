#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : views_utils.py
@Author: HP.Liew
@Date  : 2019/11/15 10:43
@Desc  : 
'''

from EasyWork.utils.database_ops import *
from django.core.cache import cache


def simpleQuery(request, tablename, prefix=''):
    columnNames = []
    columnValues = []
    simpleValue = []

    if request.method == 'GET':
        columnname1 = request.GET.get('%scolumnname1' % prefix, '').strip()
        columnname2 = request.GET.get('%scolumnname2' % prefix, '').strip()
        columnvalue1 = request.GET.get('%scolumnvalue1' % prefix, '').strip()
        columnvalue2 = request.GET.get('%scolumnvalue2' % prefix, '').strip()

        if columnname1 and columnvalue1:
            columnNames.append(columnname1)
            columnValues.append(columnvalue1)
        elif columnvalue1 and not columnname1:
            simpleValue.append(columnvalue1)
        if columnname2 and columnvalue2:
            columnNames.append(columnname2)
            columnValues.append(columnvalue2)
        elif columnvalue2 and not columnname2:
            simpleValue.append(columnvalue2)

    if len(columnNames) == 1:
        dataList = getSingleData(tableName=tablename, columnName=columnNames[0], columnValue=columnValues[0]).values()
    elif len(columnNames) == 2:
        dataList = getDoubleData(tableName=tablename, columnNames=columnNames, columnValues=columnValues).values()
    elif len(simpleValue) == 1:
        dataList = getReSingleData(tableName=tablename, value=simpleValue[0]).values()
    else:
        dataList = getAll(tablename).values()
    return dataList, '-'.join(columnValues)


def intervalQuery(request):
    if request.method == 'GET':
        startYear = request.GET.get('startyear').strip()
        endYear = request.GET.get('endyear').strip()
    return getErpPrescrapData(endYear=endYear, startYear=startYear).values(), startYear + '-' + endYear


def basicStatisticData():
    # 查询数据表数据条数
    if not cache.get('erpCount'):
        cache.set('schedualCount', countAll('schedual'), 24 * 60 * 60)
        cache.set('erpCount', countAll('erp'), 24 * 60 * 60)
        cache.set('scrapedCount', countAll('scraped'), 24 * 60 * 60)
        cache.set('inventoriedCount', countAll('inventory'), 24 * 60 * 60)

    typesStatic = countColumn('schedual', 'other_attachment').values()  # 办公类、生产类、无形类资产
    staffProductStatic = countAggregateColumn('schedual', 'staff_name', 'other_attachment', '生产').values()[
                         :9]  # 办公类、生产类、无形类资产
    staffOfficeStatic = countAggregateColumn('schedual', 'staff_name', 'other_attachment', '办公').values()[
                        :9]  # 办公类、生产类、无形类资产
    addressStatic = {}
    addressLabels = ['国通', '梅林', '澳知浩', 'NEO', '南方基地', '广州', '北京']
    for al in addressLabels:
        addressStatic[al] = countColumn('schedual', 'address', al)
    return
