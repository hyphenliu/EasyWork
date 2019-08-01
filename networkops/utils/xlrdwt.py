import xlsxwriter
import xlrd
from xlrd.xldate import xldate_as_datetime


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
