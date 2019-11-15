#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : database_ops.py
@Author: HP.Liew
@Date  : 2019/11/14 16:38
@Desc  : 
'''
from django.db.models import Q, Count
from EasyWork.utils.data_struct import *
from EasyWork.utils.xlrdwt import *
from functools import reduce
import operator


def countAll(tableName):
    return tableClass[tableName].objects.count()


def countColumn(tableName, columnName, columnValue):
    return tableClass[tableName].objects.filter(**{columnName + '__icontains': columnValue}).count()


def countAggregateColumn(tableName, columnName):
    return tableClass[tableName].objects.values_list(columnName).annotate(num=Count(columnName)). \
        values(columnName, "num").order_by("-num")


def countAggregateColumn(tableName, columnName, filterColumn, filterValue):
    return tableClass[tableName].objects.filter(**{filterColumn + '__icontains': filterValue}).values_list(
        columnName).annotate(num=Count(columnName)).values(columnName, "num").order_by("-num")


###############################################################################################
def importDatabase(tableName, datas, dropTable=False, dropTime=False):
    '''
    批量导入到数据表中，区分传入数据的类型未字典还是列表
    :param tableName:
    :param datas:
    :param dropTable:
    :return:
    '''
    vars = tableColums[tableName]
    model = tableClass[tableName]
    dataList = []
    if dropTable:  # 需要清空数据表
        model.objects.all().delete()
    if dropTime:
        today = datetime.date.today()
        model.objects.filter(update=today).delete()
    if isinstance(datas, list):
        for data in datas:
            if isinstance(data, list):
                lineDict = dict(zip(vars, data))
                dataList.append(model(**lineDict))
            elif isinstance(data, dict):
                dataList.append(model(**data))
    elif isinstance(datas, dict):
        for k, v in datas.items():
            dataList.append(model(**v))
    try:
        model.objects.bulk_create(dataList)
        return True
    except Exception as e:
        print(e)
        return False


def insertBulk(tableName, datas):
    """
    已经配对好的数据插入到数据库中
    :param tableName:
    :param datas: [{k1:v1},{k2,v2}...]
    """
    model = tableClass[tableName]
    datas = [model(**data) for data in datas]
    try:
        model.objects.bulk_create(datas)
        return True
    except Exception as e:
        print(e)
        return False


def addSingle(tableName, data):
    '''
    data要为字典格式
    :param tableName:
    :param data:
    :return:
    '''
    model = tableClass[tableName]
    try:
        model.objects.create(**data)
    except Exception as e:
        print('[DB ERROR] insert %s failed. %s' % (data, e))


def updateBulk(tableName, datas, column):
    '''
    根据表名和字段批量更新数据库，传入的必须是字典数据
    :param tableName:
    :param datas:
    :param column: 指定列
    :return:
    '''
    model = tableClass[tableName]
    for data in datas:
        if isinstance(column, list):  # 多个字段组合为唯一值
            Q_filter = reduce(operator.and_, [Q(**{"{}__exact".format(x): data[x]}) for x in column])
            item = model.objects.filter(Q_filter)
        else:
            item = model.objects.filter(Q(**{column + '__exact': data[column]}))
        try:
            item.update(**data)
        except Exception as e:
            print('[DB ERROR] update %s failed. %s' % (data, e))
            return False
    return True


def updateSingle(tableName, data, column):
    '''
    单独更新，传入数据为字典格式
    :param tableName:
    :param data:
    :param column:
    :return:
    '''
    model = tableClass[tableName]
    if isinstance(column, list):  # 多个字段组合为唯一值
        Q_filter = reduce(operator.and_, [Q(**{"{}__exact".format(x): data[x]}) for x in column])
        item = model.objects.filter(Q_filter)
    else:
        item = model.objects.filter(Q(**{column + '__exact': data[column]}))
    try:
        item.update(**data)
    except Exception as e:
        print('[DB ERROR] update %s failed. %s' % (data, e))


#################################################################################
def getAllForColumns(tableName, columns):
    '''
    返回指定N个字段，以资产标签为key，value为指定字段
    :param tableName:数据表名
    :param columns:需要的数据
    :return:{asset_label:columns}
    '''
    result = {}
    if ('asset_label' in columns) or ('early_label' in columns):
        if 'asset_label' in columns:
            index = columns.index('asset_label')
        else:
            index = columns.index('early_label')
    else:
        index = 0
        columns.insert(0, 'asset_label')

    columns = tuple(columns)
    dataSets = tableClass[tableName].objects.all().values_list(*columns)
    for ds in dataSets:
        result[ds[index]] = ds

    return result


def getAllForColumns(tableName, columns, order_column='id'):
    '''
    返回指定N个字段，以资产标签为key，value为指定字段
    :param tableName:数据表名
    :param columns:需要的数据
    :return:{asset_label:columns}
    '''
    result = {}
    index = 0
    columns.insert(0, order_column)
    columns = tuple(columns)
    dataSets = tableClass[tableName].objects.all().values_list(*columns)
    for ds in dataSets:
        result[ds[index]] = ds

    return result


def getAll(tableName):
    '''
    通过Django Models获取数据表中所有的数据
    :param tableName:
    :return:
    '''
    if tableName in ['erp', 'schedual', 'inventoried', 'inventory', 'prescap', 'scraped']:
        return tableClass[tableName].objects.all().order_by('asset_label')
    return tableClass[tableName].objects.all()


def getDoubleData(tableName, columnNames, columnValues):
    '''
    同时查询2个字段，并返回结果
    :param tableName:数据表
    :param columnNames:需要查询的字段列表
    :param columnValues:需要查询的值列表
    :return:
    '''
    if tableName in ['erp', 'schedual', 'inventoried', 'inventory', 'prescap', 'scraped']:
        if 'asset_label' in columnNames:  # 需要同时查询历史资产标签号
            cIndex = columnNames.index('asset_label')
            cv1 = columnValues[cIndex]
            columnNames.remove('asset_label')
            columnValues.remove(cv1)
            if tableName == 'erp':
                resultSets = tableClass[tableName].objects.filter(
                    Q(**{'asset_label__icontains': cv1}) | Q(**{'early_label__icontains': cv1}),
                    Q(**{columnNames[0] + '__icontains': columnValues[0]})).order_by('asset_label')
            elif tableName == 'schedual':
                resultSets = tableClass[tableName].objects.filter(
                    Q(**{'asset_label__icontains': cv1}) | Q(**{'note__icontains': cv1}),
                    Q(**{columnNames[0] + '__icontains': columnValues[0]})).order_by('asset_label')
            else:
                resultSets = tableClass[tableName].objects.filter(Q(**{'asset_label__icontains': cv1}),
                                                                  Q(**{columnNames[0] + '__icontains': columnValues[
                                                                      0]})).order_by('asset_label')
        else:
            resultSets = tableClass[tableName].objects.filter(Q(**{columnNames[0] + '__icontains': columnValues[0]}),
                                                              Q(**{columnNames[1] + '__icontains': columnValues[
                                                                  1]})).order_by('asset_label')
    else:
        resultSets = tableClass[tableName].objects.filter(Q(**{columnNames[0] + '__icontains': columnValues[0]}),
                                                          Q(**{columnNames[1] + '__icontains': columnValues[1]}))
    return resultSets


def getExactlySingle(tableName, columnName, columnValue):
    '''
    精确查找某个字段的某个值，结果可以是多条数据
    :param tableName: 数据库表
    :param columnName: 字段名
    :param columnValue: 字段值
    :return:
    '''
    if 'asset_label' == columnName:
        if tableName == 'schedual':
            return tableClass[tableName].objects.filter(
                Q(**{'asset_label__icontains': columnValue}) | Q(**{'note__iexact': columnValue})).order_by(
                'asset_label')
        if tableName == 'erp':
            return tableClass[tableName].objects.filter(
                Q(**{'asset_label__iexact': columnValue}) | Q(**{'early_label__iexact': columnValue})).order_by(
                'asset_label')
    return tableClass[tableName].objects.filter(**{columnName + '__iexact': columnValue}).order_by('asset_label')


def getSingleData(tableName, columnName, columnValue):
    '''
    获取包含某个值的结果，返回查找结果，结果可以是多条数据
    :param tableName:数据库表
    :param columnNames:字段名
    :param columnValues:字段值
    :return:
    '''
    if tableName in ['erp', 'schedual', 'inventoried', 'inventory', 'prescap', 'scraped']:
        if 'asset_label' == columnName:  # 需要同时查询历史资产标签号
            if tableName == 'erp':
                resultSets = tableClass['erp'].objects.filter(
                    Q(**{'asset_label__icontains': columnValue}) | Q(
                        **{'early_label__icontains': columnValue})).order_by('asset_label')
            elif tableName == 'schedual':
                resultSets = tableClass[tableName].objects.filter(
                    Q(**{'asset_label__icontains': columnValue}) | Q(**{'note__icontains': columnValue})).order_by(
                    'asset_label')
            else:
                resultSets = tableClass[tableName].objects.filter(**{'asset_label__icontains': columnValue}).order_by(
                    'asset_label')
        else:
            resultSets = tableClass[tableName].objects.filter(**{columnName + '__icontains': columnValue}).order_by(
                'asset_label')
    else:
        resultSets = tableClass[tableName].objects.filter(**{columnName + '__icontains': columnValue})

    return resultSets


def getReSingleData(tableName, value):
    '''
    获取包含某个值的结果，不限定字段，返回查找结果，结果可以是多条数据
    :param tableName:
    :param value:
    :return:
    '''
    columns = htmlColums[tableName]
    Q_filter = reduce(operator.or_, [Q(**{"{}__iregex".format(key): value}) for key in columns])
    resultSets = tableClass[tableName].objects.filter(Q_filter)
    return resultSets


######################################################################################
# inventory statistic
def queryUninventoriedData():
    '''
    1. 从ERP中获取生产类资产
    2. 从盘点结果中筛选生产类资产
    3. 从盘点清册中剔除清册之外的资产
    最终返回应盘点到，但未盘到到资产
    :return:
    '''
    pList = {}
    iList = []
    resultData = []
    productList = getSingleData('erp', 'other_attachment', '生产').values_list('asset_label', 'model',
                                                                             'staff_name').values()
    inventoryList = getSingleData('inventoried', 'note', '生产').values_list('asset_label', 'staff_name').values()
    for pl in productList:
        pList[pl['asset_label']] = [pl['model'], pl['staff_name']]
    for il in inventoryList:
        if il['asset_label'] in pList:
            del pList[il['asset_label']]
        else:
            iList.append(il['asset_label'])
    for k, v in pList.items():
        item = getSingleData('schedual', 'asset_label', k).values()
        if not item:
            continue
        item = item[0]
        resultData.append([k, item['asset_name'], item['model'], item['manufactor'], item['address'],
                           item['staff_department'], item['staff_name'], item['note']])
    return resultData


def filterInventoriedData():
    '''
    1. 从盘点结果中获取生产类资产
    2. 从ERP中获取生产类资产
    3. 比对资产责任人、资产型号、资产位置信息是否发生变动
    :return:
    '''
    resultData = []
    erpData = getAllForColumns('erp', ['asset_label', 'model', 'staff_name', 'staff_code', 'address'])
    inventoriedData = getAllForColumns('inventoried', ['asset_label', 'model', 'staff_name', 'address'])
    repeatList = getSingleData('inventoried', 'note', '标签重复').values_list('asset_label')
    repeatList = [i[0] for i in set(repeatList)]
    for ki, vi in inventoriedData.items():
        if ki in repeatList: continue
        note = ''
        vi = list(vi)
        vi[-1] = vi[-1].split()[0]
        if ki in erpData:
            staff1, staff2 = inventoriedData[ki][2], erpData[ki][2]
            if not staff1 == staff2:
                note = note + '|责任人变更'
            model1, model2 = inventoriedData[ki][1], erpData[ki][1]
            if not model1.replace(' ', '').lower() == model2.replace(' ', '').lower():
                note = note + '|型号变更'
            address1, address2 = inventoriedData[ki][-1].split()[0].replace('.', ''), erpData[ki][-1].split('.')[0]
            if not ((address1 in address2) or (address2 in address1)):
                note = note + '|位置变更'
            vi.extend([model2, staff2, address2])
            vi.append(note.strip('|'))
            resultData.append(vi)
    return resultData


def getErpPrescrapData(endYear=False, startYear=False):
    '''
    获取指定时间段应该报废的资产
    :param endYear:yyyy
    :param startYear:yyyy
    :return:[['资产标签号','资产名称','规格型号','厂商','按比例分摊日期','使用年限','员工编号','员工姓名']……]
    '''
    if not endYear:
        endYear = datetime.datetime.today().date()
    else:
        endYear = datetime.datetime.strptime(endYear, '%Y-%m')
    if startYear:
        startYear = datetime.datetime.strptime(startYear, '%Y-%m')
        if endYear < startYear:
            endYear, startYear = startYear, endYear
    # updateERPDepreciateDate()
    if not startYear:
        resultSets = tableClass['erp'].objects.filter(**{'scrap_date__lte': endYear}).order_by('asset_label')
    else:
        resultSets = tableClass['erp'].objects.filter(**{'scrap_date__range': [startYear, endYear]}).order_by(
            'asset_label')
    return resultSets


def updateInventoried():
    '''更新盘点结果表，从ERP补充数据字段信息。因为盘点的时候只记录资产标签号，不记录其他信息，需要补充'''
    inventoryDataSets = getAll('inventory').values()
    for ids in inventoryDataSets:
        updateItem = {}
        if not re.search(r'^[CMSZXMLG\d-]+?', ids['asset_label']):  # 匹配具有实际资产编号的资产
            continue
        erpLine = getExactlySingle('scraped', 'asset_label', ids['asset_label']).values()
        if erpLine:
            updateItem['note'] = '应为已报废资产'
            obj = tableClass['inventory'].objects.filter(id=ids['id'])
            obj.update(**updateItem)
            continue
        try:
            erpLine = getExactlySingle('schedual', 'asset_label', ids['asset_label']).values()[0]
        except:
            updateItem['note'] = '不在盘点清册中'
        else:
            updateItem['asset_name'] = erpLine['asset_name']
            updateItem['model'] = erpLine['model']
            updateItem['manufactor'] = erpLine['manufactor']
        obj = tableClass['inventory'].objects.filter(id=ids['id'])
        obj.update(**updateItem)


def updateERPDepreciateDate():
    '''
    更新ERP中资产的减值等信息
    :return:
    '''
    dataSets = getAll('erp')
    print('starting update erp deprecate......')
    for ds in dataSets.values():
        depreciateDate = ds['depreciate_date']  # 按比例分摊日期
        depreciateDate = depreciateDate.strftime('%Y-%m-%d')
        limitYear = ds['limit_year']  # 使用年限
        cost = ds['cost']  # 成本
        ds['remainder_month'], ds['cost'], ds['remainder_value'], ds['remainder_count'], ds['residual_value'], \
        ds['month_depreciate'], ds['year_depreciate'], ds['accumulate_depreciate'] = \
            reCalculateERPCost(1, depreciateDate, limitYear, cost)
        obj = tableClass['erp'].objects.filter(id=ds['id'])
        obj.update(**ds)
    print('udpate erp deprecate finished!')

# updateERPDepreciateDate()
# getErpPrescrapData(endYear=2010, startYear=2011)
# updateInventoried()
