from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import json
# Create your views here.
# from EasyWork.utils.logger import logger
from dailywork.utils.contact_information import OA
from dailywork.utils.views_utils import *
from EasyWork.utils.json_datetime import DatetimeEncoder
from EasyWork.utils.file_operator import export2Xls

@login_required
def weeklyReport(request):
    return render(request, 'pages/dailywork_weekly_report.html')

@login_required
def taxiList(request):
    return render(request, 'pages/dailywork_taxi_list.html')

@login_required
def taxi_ajax(request, tablename):
    if request.is_ajax():
        error = ''
        month = request.GET.get('selectedMonth', 200)
        item_limit = request.GET.get('itemLimit', 200)
        total_limit = request.GET.get('totalLimit', '')
        day_list = request.GET.get('daylist', '')
        if not item_limit:
            error = error + '<p>请填写单张额度</p>'
        else:
            item_limit = int(item_limit)
        if not total_limit:
            error = error + '<p>请填写总额度</p>'
        else:
            total_limit = int(total_limit)
        if not day_list:
            error = error + '<p>选择月份/日期</p>'
        else:
            day_list = day_list.split(',')
        if error:
            return HttpResponse(json.dumps({'errors': error}))

        data_list = taxiListGen(item_limit, total_limit, day_list)
        cache.set('export{}2XlsContent'.format(tablename), data_list, 60)
        cache.set('export{}2XlsName'.format(tablename), tablename + '-' + month, 60)
        return HttpResponse(json.dumps({'success': '成功生成 %s 条数据，详见下载附件' % len(data_list)}))

@login_required
def cmitcontact(request):
    tableTitle = zip(htmlTitles['contact'], htmlColums['contact'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('contact'))
    return render(request, 'pages/dailywork_cmit_contact.html',
                  {'titles': tableTitle, 'querysuccess': batchQueryStatus})

@login_required
def cmitcontact_ajax(request):
    if request.is_ajax():
        error = ''
        oauser = request.GET.get('oauser')
        oapasswd = request.GET.get('oapasswd')
        org = request.GET.get('org', '信息技术中心（公司）')
        org_type = request.GET.get('orgtype', '直属单位')
        oaurl = 'hq.cmcc'
        oa = OA(oaurl, oauser, oapasswd)
        result = oa.getContactInfo(org_type=org_type, org=org)
        try:
            importDatabase('contact', result, dropTable=True)
        except Exception as e:
            error = '导入数据库失败'
        ret = {'data': 'true', 'error': error}
        return HttpResponse(json.dumps(ret))

@login_required
def listpage(request, tablename):
    dataSets = []
    limit = 10
    offset = 0
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

    dataList, queryStr = simpleQuery(request, tablename)

    cache.set('export{}2XlsContent'.format(tablename), export2Xls('dailywork',dataList, tablename), 60)
    cache.set('export{}2XlsName'.format(tablename), tablename + '-' + queryStr, 60)

    total = dataList.count()
    try:
        paginator = Paginator(dataList, limit)
    except Exception:
        print('get %s data error' % tablename)
        return HttpResponse(json.dumps({'errors': '获取 %s 数据时出现错误' % tablename}))
    try:
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
    except:
        data = []

    for d in data:
        dataSets.append(d)

    return HttpResponse(json.dumps({'total': total, 'rows': dataSets}, cls=DatetimeEncoder))
