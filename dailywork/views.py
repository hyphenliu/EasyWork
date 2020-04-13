from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import json
import logging
# Create your views here.
from dailywork.utils.contact_information import OA
from dailywork.utils.views_utils import *
from EasyWork.utils.views_utils import *
from EasyWork.utils.data_struct import *
from EasyWork.utils.json_datetime import DatetimeEncoder
from EasyWork.utils.file_operator import export2Xls
from EasyWork.utils.passwd_ops import *
from dailywork.utils.SOX import sox_feature

logger = logging.getLogger('views')


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
        return HttpResponse(json.dumps({'success': '成功生成 {} 条数据，详见下载附件'.format(len(data_list))}))


@login_required
def sox(request):
    tableTitle = zip(htmlTitles['sox'], htmlColums['sox'])
    tips = '导入的EXCEL表头需要包含至少1/4的特征值：{}'.format('、'.join(sox_feature))
    uploadStatus = cache.get('download{0}{1}file'.format('dailywork', 'sox'))
    msg = cache.get('pageShowOn{}'.format('sox'), '')  # 获取处理结果，如错误信息，告警信息
    return render(request, 'pages/dailywork_sox_list.html',
                  {'titles': tableTitle, 'uploadsuccess': uploadStatus, 'msg': msg, 'tips': tips})


@login_required
def sox_config_ajax(request):
    if request.is_ajax:
        user = request.GET.get('oauser')
        passwd = request.GET.get('oapasswd')
        oa = OA('hq.cmcc', user, passwd)
        if not oa.paramsDict:
            return HttpResponse(json.dumps({'error': '请在内网使用本程序！'}))
        result = oa.login()
        if result['error']:
            return HttpResponse(json.dumps({'error': result['error']}))

        return HttpResponse(json.dumps({'success': '配置成功！'}))


@login_required
def sox_config(request):
    tableTitle = zip(htmlTitles['soxtasks'], htmlColums['soxtasks'])
    year = '{}'.format(datetime.date.today().year)
    month = '{:0>2}'.format(datetime.date.today().month + 1)
    if month == '12':
        year = '{}'.format(int(year) + 1)
        month = '01'
    return render(request, 'pages/dailywork_sox_task_config.html', {'titles': tableTitle, 'year': year, 'month': month})


@login_required
def cmitcontact(request):
    username = request.user.username
    publickey = genPublickey(username)  # 生成公钥加密
    tableTitle = zip(htmlTitles['contact'], htmlColums['contact'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('contact'))
    return render(request, 'pages/dailywork_cmit_contact.html',
                  {'titles': tableTitle, 'querysuccess': batchQueryStatus, 'publickey': publickey})


@login_required
def cmitcontact_ajax(request):
    if request.is_ajax():
        error = ''
        username = request.user.username
        oauser = request.GET.get('oauser', '')
        oapasswd = request.GET.get('oapasswd', '')
        if not oauser and oapasswd:
            return HttpResponse(json.dumps({'error': '用户名、密码为空！'}))
        oapasswd = dePrivatekey(oapasswd, username)  # 先解密得到明文
        org = request.GET.get('org', '信息技术中心（公司）')
        org_type = request.GET.get('orgtype', '直属单位')
        oaurl = 'hq.cmcc'
        oa = OA(oaurl, oauser, oapasswd)
        if not oa.paramsDict:
            return HttpResponse(json.dumps({'error': '请在内网使用本程序！'}))
        result = oa.getContactInfo(org_type=org_type, org=org)
        if result['error']:
            return HttpResponse(json.dumps({'error': result['error']}))
        if result['insert']:
            try:
                importDatabase(tableName='contact', datas=result['insert'], dropTable=False)
            except Exception as e:
                error = '导入数据库失败'
        if result['update']:
            try:
                updateBulk(tableName='contact', datas=result['update'], column=['department', 'email', 'phone'])
            except Exception as e:
                error = '更新数据库失败'
        ret = {'data': 'true', 'error': error}
        return HttpResponse(json.dumps(ret))


def cmitcontact_progress(request):
    p_num = cache.get('contactProgressNum', '0')
    return HttpResponse(json.dumps(p_num))


@login_required
def listpage(request, tablename):
    dataSets = []
    limit = 10
    offset = 0
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

    dataList, queryStr = simpleQuery(request, tablename)
    cache.set('export{}2XlsContent'.format(tablename), export2Xls('dailywork', dataList, tablename), 60)
    cache.set('export{}2XlsName'.format(tablename), tablename + '-' + queryStr, 60)

    total = dataList.count()
    try:
        paginator = Paginator(dataList, limit)
    except Exception:
        print('get {} data error'.format(tablename))
        return HttpResponse(json.dumps({'errors': '获取 {} 数据时出现错误'.format(tablename)}))
    try:
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
    except:
        data = []

    for d in data:
        dataSets.append(d)

    return HttpResponse(json.dumps({'total': total, 'rows': dataSets}, cls=DatetimeEncoder))
