from django.db.models import Q, Count, Sum
import datetime
from dailywork.utils.data_struct import *
from .xlrdwt import *
from functools import reduce
import operator

def importDatabase(tableName, datas, dropTable=False, dropTime=False):
    '''
    批量导入到数据表中
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
    if isinstance(datas, dict):
        for k, v in datas.items():
            dataList.append(model(**v))
    elif isinstance(datas, list):
        for data in datas:
            if isinstance(data, list):
                lineDict = dict(zip(vars, data))
                dataList.append(model(**lineDict))
            elif isinstance(data, dict):
                dataList.append(model(**data))
    try:
        model.objects.bulk_create(dataList)
        return True
    except Exception as e:
        print(e)
        return False

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
        if isinstance(column, list):# 多个字段组合为唯一值
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
    if isinstance(column, list):# 多个字段组合为唯一值
        Q_filter = reduce(operator.and_, [Q(**{"{}__exact".format(x): data[x]}) for x in column])
        item = model.objects.filter(Q_filter)
    else:
        item = model.objects.filter(Q(**{column + '__exact': data[column]}))
    try:
        item.update(**data)
    except Exception as e:
        print('[DB ERROR] update %s failed. %s' % (data, e))
#################################################################################
def getAll(tableName):
    '''
    通过Django Models获取数据表中所有的数据
    :param tableName:
    :return:
    '''
    return tableClass[tableName].objects.all()


def getDoubleData(tableName, columnNames, columnValues):
    '''
    同时查询2个字段，并返回结果
    :param tableName:数据表
    :param columnNames:需要查询的字段列表
    :param columnValues:需要查询的值列表
    :return:
    '''
    resultSets = tableClass[tableName].objects.filter(Q(**{columnNames[0] + '__icontains': columnValues[0]}),
                                                          Q(**{columnNames[1] + '__icontains': columnValues[
                                                              1]}))
    return resultSets


def getExactlySingle(tableName, columnName, columnValue):
    '''
    精确查找某个字段的某个值，结果可以是多条数据
    :param tableName: 数据库表
    :param columnName: 字段名
    :param columnValue: 字段值
    :return:
    '''

    return tableClass[tableName].objects.filter(**{columnName + '__iexact': columnValue})


def getSingleData(tableName, columnName, columnValue):
    '''
    获取包含某个值的结果，返回查找结果，结果可以是多条数据
    :param tableName:数据库表
    :param columnNames:字段名
    :param columnValues:字段值
    :return:
    '''

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