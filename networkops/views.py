from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.core.cache import cache
from playsound import playsound
import json
import re

from networkops.utils.accesslist import *
from networkops.utils.views_utils import *
from EasyWork.utils.views_utils import *
from EasyWork.utils.mail_utils import *
from EasyWork.utils.json_datetime import DatetimeEncoder
from EasyWork.utils.file_operator import export2Xls


@login_required
def access_list(request):
    return render(request, 'pages/network_access_list.html')


@login_required
def access_list_product(request):
    if request.is_ajax():
        device = request.GET.get('device')
        originalIP = request.GET.get('originalIP')
        distinateIP = request.GET.get('distinateIP')
        mask = request.GET.get('mask')
        port = request.GET.get('port')
        data, errors = complateAccessList(device, originalIP, mask, distinateIP, port)
        ret = {'data': data, 'errors': errors}
        return HttpResponse(json.dumps(ret))
    else:
        pass


@login_required
def accesslist(request):
    access_list_title = zip(htmlTitles['accesslist'], htmlColums['accesslist'])
    uploadStatus = cache.get('download{0}{1}file'.format('network', 'accesslist'))
    msg = cache.get('pageShowOn{}'.format('accesslist'), '')  # 获取处理结果，如错误信息，告警信息
    return render(request, 'pages/network_accesslist.html',
                  {'titles': access_list_title, 'msg': msg, 'uploadsuccess': uploadStatus})


@login_required
def ipmapping(request):
    ip_list_title = zip(htmlTitles['ipmapping'], htmlColums['ipmapping'])
    pat_list_title = zip(htmlTitles['ippatmapping'], htmlColums['ippatmapping'])
    uploadStatus = cache.get('download{0}{1}file'.format('network', 'ipmapping'))
    msg = cache.get('pageShowOn{}'.format('ipmapping'), '')  # 获取处理结果，如错误信息，告警信息
    return render(request, 'pages/network_ipmapping.html',
                  {'iptitles': ip_list_title, 'pattitles': pat_list_title, 'msg': msg, 'uploadsuccess': uploadStatus})


@login_required
def ipCheck(request):
    titles = zip(htmlTitles['iplist'], htmlColums['iplist'])
    return render(request, 'pages/network_ip_query.html', {'titles': titles})


@login_required
def devicecheck(request):
    return render(request, 'pages/network_devicecheck.html')


@login_required
def devicecheck_ajax(request):
    result = []
    errors = '<div style="color:red">{}</div'
    input = {'inspector': '检查人', 'checker': '复核人', 'sender': '发件人', 'mailpasswd': '邮箱密码', 'recevier': '收件人',
                  'cc': '抄送人', 'cipher': 'Cipher'}
    for k, v in input.items():
        value = request.GET.get(k, '').strip()
        if not value:
            return HttpResponse(json.dumps({'errors': errors.format('<p>{}为空</p>'.format(v))}))
        if k in ['sender','recevier','cc']:
            input[k] = getMulContactEmailAddr(re.split('[ ,，；;]',value))
        else:
            input[k] = value
        result.append('{}={}'.format(k, input[k]))
    if 'error' in checkEmailLogin(input['sender'],input['mailpasswd']):
        return HttpResponse(json.dumps({'errors': errors.format('<p>用户名或邮箱密码错误</p>')}))
    if 'error' in checkCipher(input['cipher']):
        return HttpResponse(json.dumps({'errors': errors.format('<p>Cipher密码错误</p>')}))
    with open(os.path.join(settings.CONF_DIR, 'devicecheck'), 'w+') as f:
        f.write('#'.join(result)+'#mailsign={}'.format(request.GET.get('mailsign', '')))

    return HttpResponse(json.dumps({'failed': ''}))


@login_required
def fengdu(request):
    fd_table_title = zip(htmlTitles['fengdu'], htmlColums['fengdu'])
    jf_table_title = zip(htmlTitles['jiefeng'], htmlColums['jiefeng'])
    szfd_table_title = zip(htmlTitles['jichufd'], htmlColums['jichufd'])
    szjf_table_title = zip(htmlTitles['jichujf'], htmlColums['jichujf'])
    return render(request, 'pages/network_fengdu.html',
                  {'fdtitles': fd_table_title, 'jftitles': jf_table_title, 'szfdtitles': szfd_table_title,
                   'szjftitles': szjf_table_title})


@login_required
def paicha(request):
    pc_table_title = zip(htmlTitles['paicha'], htmlColums['paicha'])
    bz_table_title = zip(htmlTitles['baozhang'], htmlColums['baozhang'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('paicha'))
    return render(request, 'pages/network_paicha.html',
                  {'pctitles': pc_table_title, 'bztitles': bz_table_title, 'querysuccess': batchQueryStatus})


@login_required
def paicha_ajax(request):
    text = request.GET.get('text').strip()
    errors, data, info = extractHuwangInfo(text)
    print(data)
    if data['paicha']:
        playsound('C:\Windows\media\Alarm05.wav')
    ret = {'errors': errors, 'data': data, 'info': info}
    return HttpResponse(json.dumps(ret))


@login_required
def listpage(request, tablename):
    dataSets = []
    limit = 10
    offset = 0
    if tablename == 'fengdu':
        prefix = 'fd'
    elif tablename == 'jiefeng':
        prefix = 'jf'
    elif tablename == 'paicha':
        prefix = 'pc'
    elif tablename == 'jichufd':
        prefix = 'szfd'
    elif tablename == 'jichujiefeng':
        prefix = 'szjf'
    elif tablename == 'baozhang':
        prefix = 'bz'
    elif tablename == 'ipmapping':
        prefix = 'ip'
    elif tablename == 'ippatmapping':
        prefix = 'pat'
    else:
        prefix = ''
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

    dataList, queryStr = simpleQuery(request, tablename, prefix)
    cache.set('export{}2XlsContent'.format(tablename), export2Xls('network', dataList, tablename), 60)
    cache.set('export{}2XlsName'.format(tablename), tablename + '-' + queryStr, 60)

    total = dataList.count()
    try:
        paginator = Paginator(dataList, limit)
    except Exception as e:
        print('get {} data error {}'.format(tablename, e))
        return HttpResponse({'errors': 'Get {} data encounter an error'.format(tablename)})
    try:
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
    except:
        data = []

    for d in data:
        dataSets.append(d)

    return HttpResponse(json.dumps({'total': total, 'rows': dataSets}, cls=DatetimeEncoder))
