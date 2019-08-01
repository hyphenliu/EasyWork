from django.db.models import Q, Count, Sum
from dailywork.utils.data_struct import *
from .xlrdwt import *

def importDatabase(tableName, datas, dropTable=False):
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
    for data in datas:
        lineDict = dict(zip(vars, data))
        dataList.append(model(**lineDict))
    try:
        model.objects.bulk_create(dataList)
        return True
    except Exception as e:
        print(e)
        return False


#################################################################################
def getAllForColumns(tableName, columns):
    '''
    返回指定N个字段，以资产标签为key，value为指定字段
    :param tableName:数据表名
    :param columns:需要的数据
    :return:{asset_label:columns}
    '''
    result = {}
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
