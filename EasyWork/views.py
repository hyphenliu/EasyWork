from django.shortcuts import render, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.http import StreamingHttpResponse
from django.utils.http import urlquote  # 导出中文文件名
from EasyWork.utils.file_operator import *
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import time
from .utils import *
from networkops.utils.feixin_extract import updateDatabase
from networkops.utils.devicecheck import CheckDevice
from inventory.utils import database_ops as assets_dbops


# try:
#     print('[INFO] Excute scheduals')
#     sched = BackgroundScheduler()
#     sched.add_jobstore(DjangoJobStore(), 'default')
#
#     @register_job(sched, 'interval', seconds=10, start_date='2019-09-19 00:00:20', end_date='2019-10-10 00:00:03')
#     def extractFeixin():
#         updateDatabase()
#     #
#     #
#     # @register_job(sched, 'interval', hours=2, start_date='2019-07-01 10:00:20', end_date='2019-07-02 00:01:00')
#     # def sendMail():
#     #     cd = CheckDevice()
#     #     cd.deviceCheck()
#     sched.add_job(updateDatabase, 'interval', id='extract feixin', seconds=10, start_date='2019-06-25 00:00:20',
#                   misfire_grace_time=30, end_date='2019-07-03 00:00:03')
#
#     register_events(sched)
#     sched.start()
# except Exception as e:
#     print('[ERROR] Excute schedual error. %s' % e)
#     sched.shutdown()


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
            data = assets_dbops.queryUninventoriedData()
        elif filename == '盘点信息更新':
            data = assets_dbops.filterInventoriedData()
    else:
        data = []
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;fileName="{0}.xls"'.format(urlquote(filename))
    output = responseXls(module, tableName, data, filename)
    response.write(output.getvalue())
    return response


@login_required
def uploadFile(request, module, tableName):
    '''
    处理不同类型的文件上传，1. 上传到数据库中的文件；2.上传批量查询文件
    :param request:
    :param module:模块名（暂时无实际作用）
    :param tableName: 数据库表名
    :return:
    '''
    fileName = cache.get('%s-fileName' % module)
    action = cache.get('%s-action' % module)
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
        cache.set('%s-fileName' % module, fileName, 2 * 60)
        cache.set('%s-action' % module, action, 2 * 60)

    return render(request, 'pages/upload_file.html',
                  {'module': module, 'filename': fileName, 'tablename': tableName})


@login_required
def exportExcel(request, module, tableName):
    dataName = cache.get('export{}2XlsName'.format(tableName))
    data = cache.get('export{}2XlsContent'.format(tableName))
    dateStr = time.strftime('_%Y%m%d-%H%M%S', time.localtime(time.time()))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;fileName="{0}.xls"'.format(urlquote(tableName + dateStr))
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
