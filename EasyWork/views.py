import json
import random
import time
import logging

from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.utils.http import urlquote  # 导出中文文件名

from EasyWork.utils.file_operator import *

logger = logging.getLogger('views')


@login_required
def index(request):
    return render(request, 'snippet/index.html')


@login_required
def downloadFile(request, module, tableName):
    if module == 'dailywork':
        filename = cache.get('download{0}{1}file'.format(module, tableName))
        downloadFile = os.path.splitext(filename.split(os.sep)[-1])[0]
    else:
        downloadFile = request.GET['filename']
        filename = os.path.join(settings.DOWNLOAD_DIRS, downloadFile + '.xlsx')
    response = StreamingHttpResponse(readFile(filename))
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment;filename="{0}.xlsx"'.format(urlquote(downloadFile))
    return response


@login_required
def downloadExcel(request, module, tableName):
    filename = request.GET['filename']
    if not filename:
        return
    if tableName == 'inventoried':
        if filename == '未盘点到资产下载':
            data = queryUninventoriedData()
        elif filename == '盘点信息更新':
            data = filterInventoriedData()
    else:
        data = []
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;fileName="{0}.xls"'.format(urlquote(filename))
    output = responseXls(module, tableName, data, filename)
    response.write(output.getvalue())
    return response


@login_required
def uploadFile(request, module, tableName, tips=''):
    '''
    处理不同类型的文件上传，1. 上传到数据库中的文件；2.上传批量查询文件
    :param request:
    :param module:模块名（暂时无实际作用）
    :param tableName: 数据库表名
    :return:
    '''
    fileName = cache.get('{}-fileName'.format(module))
    action = cache.get('{}-action'.format(module))
    if request.method == 'POST':
        timeStr = time.strftime('_%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        uploadFile = request.FILES.getlist('file[]')[0]
        ufName, ufExt = os.path.splitext(uploadFile.name)
        filePath = os.path.join(settings.UPLOAD_DIRS, ufName + timeStr + ufExt)
        f = open(filePath, mode='wb')
        for i in uploadFile.chunks():
            f.write(i)
        f.close()
        dealResult = dealUploadFile(module, filePath, tableName, action, fileName)
        if not dealResult:
            print('数据导入出错！')
        else:
            print('数据导入成功！')
    elif request.method == 'GET':
        fileName = request.GET.get('filename')
        action = request.GET.get('action')
        tips = request.GET.get('tips')
        cache.set('{}-fileName'.format(module), fileName, 2 * 60)
        cache.set('{}-action'.format(module), action, 2 * 60)

    return render(request, 'pages/upload_file.html',
                  {'module': module, 'filename': fileName, 'tablename': tableName, 'tips': tips})


@login_required
def exportExcel(request, module, tableName):
    dataName = cache.get('export{}2XlsName'.format(tableName))
    data = cache.get('export{}2XlsContent'.format(tableName))
    dateStr = time.strftime('_%Y%m%d-%H%M%S', time.localtime(time.time()))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;fileName="{0}.xls"'.format(urlquote(tableName + dateStr))
    if data:
        output = responseXls(module, tableName, data, dataName)
        response.write(output.getvalue())
    return response


@login_required
def exportBatchQueryResult(request, module, tableName):
    data = cache.get('exportQuery{}2XlsContent'.format(tableName))
    dataName = cache.get('exportQuery{}2XlsName'.format(tableName))
    dateStr = time.strftime('_%Y%m%d-%H%M%S', time.localtime(time.time()))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;fileName="{0}.xls"'.format(urlquote(dataName + dateStr))
    output = responseXls(module, tableName, data, dataName)
    response.write(output.getvalue())
    return response


def randomPasswd(request):
    return render(request, 'pages/tools_randompasswd.html')


def randompasswd_ajax(request):
    pass_list = ['1234567890', 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '!@#$%+_-=']
    type = 0
    pass_str = []

    passwd_len = request.GET.get('passwdlen', '')
    az = request.GET.get('az', '')
    AZ = request.GET.get('AZ', '')
    digit = request.GET.get('09', '')
    complex = request.GET.get('complex', '')

    get_list = [digit, az, AZ, complex]
    for idx, gl in enumerate(get_list):
        if gl == 'true':
            pass_str.append(pass_list[idx])
            type += 1
    passwd = []
    for i in range(int(passwd_len)):
        for j in range(type, 0, -1):
            if i % j == 0:
                passwd.append(random.choice(pass_str[j - 1]))
                break
    random.shuffle(passwd)
    return HttpResponse(json.dumps({'passwd': ''.join(passwd)}))

# from dailywork.utils.sox_remainder import *
# from EasyWork.utils.config import *
# from EasyWork.utils.wx_reminder import wechatSender

# wechatSender('程序提醒测试')
