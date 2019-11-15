import xlsxwriter
import xlrd
from xlrd.xldate import xldate_as_datetime
import datetime
import re
import copy
from EasyWork.utils import database_ops


def readXlsQueryContent(filename):
    '''
    读取批量查询列表，只读取第一列信息
    :param filename:
    :return:
    '''
    resultList = []
    data = xlrd.open_workbook(filename)
    table = data.sheet_by_index(0)
    for i in table.col_values(0):
        try:
            i = i.strip()
        except:
            continue
        if i:
            resultList.append(i)
    return resultList


def readXlsContent(filename, titleList, sheetName):
    '''
    读取指定excel文件的内容，需要给定文件标题，和文件表单sheet名。若给定的表单名在文件中能匹配到多个，则只返回第一个表单中的内容。
    :param filename: 文件全路径名
    :param titleList: 文件内容标题列，[]
    :param sheetName: 文件表单sheet名（非完全匹配）
    :return:
    '''
    data = xlrd.open_workbook(filename)
    tableNames = data.sheet_names()
    # 先找到表单，若文件只有一个表单，则直接读取该表单数据，否则按表单名称查找
    if len(tableNames) == 1:
        tablename = tableNames[0]
    else:
        for tn in tableNames:
            tn = tn.lower()
            if not sheetName in tn:
                tablename = ''
                continue
            else:
                tablename = tn
                break
    if not tablename:  # 没有找到对应的表单名，就读取第一个表单内容
        tablename = tableNames[0]

    table = data.sheet_by_name(tablename)

    return readSheetContent(table, titleList)


def readSheetContent(table, titleList=[]):
    '''
    读取表单内容
    :param table: 表单对象
    :return:
    '''
    resultData = []
    if titleList:
        listLen = len(titleList)
    else:
        listLen = 1
    merged = table.merged_cells  # 跳过表单前面的表头合并单元格
    if merged:
        nrows = merged[-1][0] if table.nrows == merged[-1][1] else table.nrows
    else:
        nrows = table.nrows
    # 严格匹配表头
    dataBegin = False
    for i in range(nrows):
        rowList = table.row_values(i)[:listLen]
        rowContent = []
        if titleList == rowList:  # 寻找有效数据开始行
            dataBegin = True
            continue
        if dataBegin:
            for j in range(listLen):
                dataType = table.cell(i, j).ctype  # 类型： 0 empty,1 string, 2 count, 3 date, 4 boolean, 5 error
                dataCell = table.cell_value(i, j)
                if dataType == 2 and dataCell % 1 == 0:
                    dataCell = int(dataCell)
                elif dataType == 3:
                    date = xldate_as_datetime(dataCell, 0)
                    dataCell = date.strftime('%Y-%m-%d')
                elif dataType == 4:
                    dataCell == True if dataCell == 1 else False
                rowContent.append(dataCell)
            resultData.append(rowContent)
    return resultData


def writeXlsContent(fileName, xlsContent, titles, sheetName='Sheet1'):
    workBook = xlsxwriter.Workbook(fileName)
    sheet = workBook.add_worksheet(sheetName)
    for t in range(len(titles)):
        sheet.write(0, t, titles[t])
    for r in range(len(xlsContent)):
        for c in range(len(r)):
            sheet.write(r + 1, c, xlsContent[r][c])
    workBook.close()


def comleteSchedualInformation(xlsData):
    resultSets = []
    erpData = database_ops.getAllForColumns('erp', ['asset_label', 'other_attachment'])
    erpData2 = database_ops.getAllForColumns('erp', ['early_label', 'other_attachment'])
    for xd in xlsData:
        if xd[0] in erpData:
            xd[-1] = xd[-1] + '|' + erpData[xd[0]][-1]
        elif xd[0] in erpData2:
            xd[-1] = xd[-1] + '|' + erpData2[xd[0]][-1]
        else:
            xd[-1] = xd[-1] + '|资产标签号不在ERP中'
        resultSets.append(xd)
    return resultSets


def complteInventoriedInformation(xlsData):
    '''
    根据实际盘点结果生产盘点最终结果
    :param xlsData:
    :return:
    'inventory': ['machine_address', 'machine_room', 'machine_column', 'machine_racket', 'asset_label', 'asset_name',
                  'model', 'manufactor', 'note', 'inventory_date'],
    'inventory': ['机房地点', '机房位置', '机架列', '机架号', '资产编码', '资产名称', '资产型号', '设备制造商', '备注'],
    'schedual': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'schedual': ['asset_label', 'asset_name', 'model', 'manufactor', 'address', 'staff_department', 'staff_name',
                 'note', 'schedual_date'],
    '''
    resultData = []
    duplicateList = []
    labelList = []
    schedualDataSets = database_ops.getAllForColumns('schedual',
                                                     ['asset_label', 'asset_name', 'model', 'manufactor', 'address',
                                                      'staff_department', 'staff_name', 'note'])
    # erpDataSets = database_ops.getAllForColumns('erp', ['asset_label', 'other_attachment'])
    # erpDataSets2 = database_ops.getAllForColumns('erp', ['early_label', 'other_attachment'])
    # 获取重复标签
    for xd in xlsData:
        xd = [str(d).strip() for d in xd]  # 删除字段的前后空格
        xd[4] = xd[4].upper()
        xd[-1] = xd[-1].upper()
        if re.search(r'^[CMSZXMLG\d-]+?$', xd[4]):  # 查找资产编码，含补充的资产编码
            asset_label = xd[4]
        elif re.search(r'^[CMSZXMLG\d-]+?$', xd[-1]):
            asset_label = xd[-1]
        else:
            continue
        if asset_label in labelList:
            duplicateList.append(asset_label)
        labelList.append(asset_label)

    for xd in xlsData:
        note = xd[-1]
        # 删除字段的前后空格
        xd = [str(d).strip() for d in xd]
        xd[4] = xd[4].upper()
        xd[-1] = xd[-1].upper()
        # 查找资产编码，含补充的资产编码
        if re.search(r'^[CMSZXMLG\d-]+?$', xd[4]):
            asset_label = xd[4]
        elif re.search(r'^[CMSZXMLG\d-]+?$', xd[-1]):
            asset_label = xd[-1]
            note = note + '|责任人补充'
        else:
            if re.search(r'[CMSZXMLG\d-]+?', xd[-1]):
                print(xd[-1])
            elif re.search(r'[CMSZXMLG\d-]+?', xd[4]):
                print(xd[4])
            continue
        # 拼接位置信息
        if xd[1]:
            address = xd[0] + '.' + xd[1] + ' ' + xd[2] + '-' + xd[3]
        else:
            address = xd[0] + ' ' + xd[2] + '-' + xd[3]
        address = address.strip('-').strip(' ').strip('.')
        # 查询盘点清册
        if asset_label in schedualDataSets:
            item = schedualDataSets[asset_label]
            note = note + item[-1]
        else:
            s_item = database_ops.getSingleData('schedual', 'note', asset_label)
            if s_item:
                items = s_item.values()[0]
                item = [items['asset_label'], items['asset_name'], items['model'], items['manufactor'],
                        items['address'], items['staff_department'], items['staff_name'], items['note']]
                note = note + item[-1]
            else:
                note = note + '|不在盘点清册'
                resultData.append([asset_label, xd[5], xd[6], xd[7], address, '', '', note.strip('|')])
                continue
        # # 获取资产类别：办公/生产/无形
        # if asset_label in erpDataSets:
        #     note = note + '|' + erpDataSets[asset_label][-1]
        # elif asset_label in erpDataSets2:
        #     note = note + '|' + erpDataSets2[asset_label][-1]
        # else:
        #     note = note + '|不在ERP中'
        # 默认同一资产在不同地方出现，则与盘点清册记录的地址信息不符的资产为标签重复
        if asset_label in duplicateList:
            note = note + '|资产标签重复'
            for i in ['国通', '东莞', '澳知浩', 'NEO', '梅林', '南方基地']:
                if i in item[4]:
                    if i in address:
                        note = note + '|该标签可能正确'
                    break
        # 资产名称
        asset_name = item[1]
        # 资产规格
        if xd[6] and not xd[6] == item[2]:
            model = xd[6]
        else:
            model = item[2]
        # 资产厂商
        if xd[7] and not xd[7] == item[3]:
            manufactor = xd[7]
        else:
            manufactor = item[3]
        # 资产责任人和资产责任人所在部门
        if xd[8]:
            staff_name = xd[8]
            staff_department = item[5]
        else:
            staff_name = item[6]
            staff_department = item[5]
        resultData.append(
            [asset_label, asset_name, model, manufactor, address, staff_department, staff_name, note.strip('|')])

    return resultData


def completeErpInformation(xlsData):
    '''
    补全ERP信息，拆分连续资产编号，更新资产减值信息，以及初步区分办公类和生产类资产
    :param xlsData:
    :return:
    '''
    resultData = []
    for xd in xlsData:

        xd[1] = xd[1].upper()
        xd[32] = xd[32].upper()
        asset_label = xd[1]  # 资产标签
        his_lablel = xd[32]
        cost = xd[17]  # 成本
        depreciateDate = xd[13]  # 按比例分摊日期
        limitYear = xd[15]  # 使用年限
        if re.match(r'^\D.*-', asset_label):
            count = xd[9]  # 数量
        else:
            count = 1
        # 根据项目名称或资产类别区分生产类资产和办公类资产，并将结果填写到other_attachment中
        if not xd[38]:  # 未区分办公和生产
            type = xd[3].split('-')[0].split('.')[-1]
            if ('零购' in xd[37]) or (type in ['07', '08', '09', '10']):
                xd[38] = '办公类资产'
            elif type in ['01', '02', '03', '04', '05', '06']:
                xd[38] = '生产类资产'
            elif type == '80':
                xd[38] = '无形资产'
        if xd[38] == '无形资产':
            bottomDiscount = 0.0
        else:
            bottomDiscount = 0.03
        xd[16:24] = reCalculateERPCost(count, depreciateDate, limitYear, cost, bottomDiscount=bottomDiscount)
        xd.append(calculateScrapDate(depreciateDate, limitYear))  # 添加可报废日期


        if re.match(r'^\D.*-', asset_label):  # 连续编号的资产标签编码
            histList = []
            nowList = continuecount(asset_label)
            if re.match(r'^[CMSZXMLG\d-]+?$', his_lablel):
                hisFlag = True
            if hisFlag and re.match(r'^\D.*-', his_lablel):  # 连续编号的资产标签编码
                histList = continuecount(his_lablel)
            if len(histList) == len(nowList):

                for i in range(len(nowList)):
                    xd[1] = nowList[i]
                    xd[32] = histList[i]
                    xd0 = copy.deepcopy(xd)
                    resultData.append(xd0)
            else:
                for i in nowList:
                    xd[1] = i
                    xd0 = copy.deepcopy(xd)
                    resultData.append(xd0)
        else:
            resultData.append(xd)
    return resultData


def continuecount(countStr):
    """
    拆分连续的资产标签号
    :param countStr: 传入的连续资产标签号 如，XM000001-0010
    :return:返回拆分后的列表list
    """
    countList = []
    code, codeTail = countStr.split('-')
    codePre = code[:-len(codeTail)]
    codeStart = int(code[len(codePre):])
    tailLen = len(codeTail)
    codeTail = int(codeTail)
    for i in range(codeStart, codeTail + 1):
        countList.append(codePre + '0' * (tailLen - len(str(i))) + str(i))
    return countList


def calculateScrapDate(depreciateDate, limitYear):
    '''计算可报废日期'''
    date = depreciateDate.split('-')
    date[0] = str(int(date[0]) + int(limitYear))
    dateStr = '-'.join(date)
    try:  # 检测2月29日
        datetime.datetime.strptime('-'.join(date), '%Y-%m-%d')
    except:
        dateStr = date[0] + '-' + date[1] + '-' + str(int(date[2]) - 1)
    return dateStr


def reCalculateERPCost(count, depreciateDate, limitYear, cost, bottomDiscount=0.03):
    '''
    根据成本、使用年限、启用日期计算【单台资产】剩余月数净值/净额/残值/本期折旧额/累计折旧额
    :param count: 资产数量
    :param depreciateDate: 折旧平摊日期
    :param limitYear: 使用年限
    :param cost: 成本
    :param bottomDiscount: 残值，固定资产为3%，无形资产为0%
    :return: 剩余月数/净值/净额/残值/本期折旧额/累计折旧额 列表
    '''
    cost = round(cost / count, 2)  # 计算单位资产的成本
    dateNow = datetime.datetime.now().strftime('%Y-%m-%d')  # 获取当前的日期
    usedMonth = countMonth(dateNow, depreciateDate)  # 获取资产正式服役的月份
    if usedMonth >= limitYear * 12:  # 计算剩余折算月份
        lastMonth = 0
    else:
        lastMonth = limitYear * 12 - usedMonth
    costPerMonth = round((cost * 0.97) / (limitYear * 12), 2)  # 每个月的折旧额
    # 计算残值
    uncost = round(cost * bottomDiscount, 2)
    # 计算净值/净额
    if lastMonth == 0:
        lastcost = round(cost * bottomDiscount, 2)
    else:
        lastcost = round(cost * bottomDiscount + costPerMonth * lastMonth, 2)
    # 计算本期折旧
    if lastMonth > 0:
        thisMonthCost = costPerMonth
    elif (limitYear * 12 - 1) == usedMonth:
        thisMonthCost = costPerMonth
    else:
        thisMonthCost = 0
    # 计算本年折旧
    limitYeartr = datetime.datetime.now().strftime('%Y') + '-1-1'
    lastYearUsedMonth = countMonth(limitYeartr, depreciateDate)
    thisYearUsedMonth = countMonth(dateNow, limitYeartr)
    if lastYearUsedMonth >= limitYear * 12:
        thisYearCost = 0
    elif (lastYearUsedMonth + thisYearUsedMonth) >= (limitYear * 12):
        thisYearCost = round((limitYear * 12 - lastYearUsedMonth) * costPerMonth, 2)
    else:
        thisYearCost = round(thisYearUsedMonth * costPerMonth, 2)
    # 计算累计折旧
    calculateCost = round(cost - lastcost, 2)

    resultList = [lastMonth, cost, lastcost, lastcost, uncost, thisMonthCost, thisYearCost, calculateCost]

    return resultList


def countMonth(str1, str2):
    """
    计算两个日期之间的月份
    :return:返回月份值
    """
    year1 = datetime.datetime.strptime(str1[0:10], "%Y-%m-%d").year
    year2 = datetime.datetime.strptime(str2[0:10], "%Y-%m-%d").year
    month1 = datetime.datetime.strptime(str1[0:10], "%Y-%m-%d").month
    month2 = datetime.datetime.strptime(str2[0:10], "%Y-%m-%d").month
    num = (year1 - year2) * 12 + (month1 - month2)
    return num
