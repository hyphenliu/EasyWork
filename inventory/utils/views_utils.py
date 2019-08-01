from inventory.utils.database_ops import *
from django.core.cache import cache


def intervalQuery(request):
    if request.method == 'GET':
        startYear = request.GET.get('startyear').strip()
        endYear = request.GET.get('endyear').strip()
    return getErpPrescrapData(endYear=endYear, startYear=startYear).values(), startYear + '-' + endYear


def simpleQuery(request, tablename):
    columnNames = []
    columnValues = []
    if request.method == 'GET':
        columnname1 = request.GET.get('columnname1').strip()
        columnname2 = request.GET.get('columnname2').strip()
        columnvalue1 = request.GET.get('columnvalue1').strip()
        columnvalue2 = request.GET.get('columnvalue2').strip()

        if columnname1 and columnvalue1:
            columnNames.append(columnname1)
            columnValues.append(columnvalue1)
        if columnname2 and columnvalue2:
            columnNames.append(columnname2)
            columnValues.append(columnvalue2)

    if len(columnNames) == 1:
        dataList = getSingleData(tableName=tablename, columnName=columnNames[0], columnValue=columnValues[0]).values()
    elif len(columnNames) == 2:
        dataList = getDoubleData(tableName=tablename, columnNames=columnNames, columnValues=columnValues).values()
    else:
        dataList = getAll(tablename).values()

    return dataList, '-'.join(columnValues)


# def export2Xls(data, tablename):
#     result = []
#     columns = htmlColums[tablename]
#     for dt in data:
#         line = []
#         for i in columns:
#             line.append(dt[i])
#         result.append(line)
#     return result


def basicStatisticData():
    # 查询数据表数据条数
    if not cache.get('erpCount'):
        cache.set('schedualCount', countAll('schedual'), 24 * 60 * 60)
        cache.set('erpCount', countAll('erp'), 24 * 60 * 60)
        cache.set('scrapedCount', countAll('scraped'), 24 * 60 * 60)
        cache.set('inventoriedCount', countAll('inventory'), 24 * 60 * 60)

    typesStatic = countColumn('schedual', 'other_attachment').values()  # 办公类、生产类、无形类资产
    staffProductStatic = countAggregateColumn('schedual', 'staff_name','other_attachment','生产').values()[:9]  # 办公类、生产类、无形类资产
    staffOfficeStatic = countAggregateColumn('schedual', 'staff_name','other_attachment','办公').values()[:9]  # 办公类、生产类、无形类资产
    addressStatic = {}
    addressLabels = ['国通', '梅林', '澳知浩', 'NEO', '南方基地', '广州', '北京']
    for al in addressLabels:
        addressStatic[al] = countColumn('schedual', 'address', al)
    return
