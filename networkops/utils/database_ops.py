from django.db.models import Q, Count
from networkops.utils.data_struct import *


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


#############################################################################
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
    if isinstance(datas, list):
        for data in datas:
            lineDict = dict(zip(vars, data))
            dataList.append(model(**lineDict))
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
    model = tableClass[tableName]
    try:
        model.objects.create(**data)
    except Exception as e:
        print('[DB ERROR] insert %s failed. %s' % (data, e))


def updateBulk(tableName, datas, column):
    model = tableClass[tableName]
    for data in datas:
        item = model.objects.filter(Q(**{column + '__exact': data[column]}))
        try:
            item.update(**data)
        except Exception as e:
            print('[DB ERROR] update %s failed. %s' % (data, e))


def updateSingle(tableName, data, column):
    model = tableClass[tableName]
    item = model.objects.filter(Q(**{column + '__exact': data[column]}))
    try:
        item.update(**data)
    except Exception as e:
        print('[DB ERROR] update %s failed. %s' % (data, e))


#################################################################################
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
