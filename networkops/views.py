from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from playsound import playsound
import json

from networkops.utils.accesslist import *
from networkops.utils.views_utils import *
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
                  {'iptitles': ip_list_title, 'pattitles':pat_list_title ,'msg': msg, 'uploadsuccess': uploadStatus})

@login_required
def ipCheck(request):
    titles = zip(htmlTitles['iplist'], htmlColums['iplist'])
    return render(request, 'pages/network_ip_query.html', {'titles': titles})


@login_required
def devicecheck(request):
    return render(request, 'pages/network_devicecheck.html')


@login_required
def devicecheck_ajax(request):
    errors = ''
    inspector = request.GET.get('inspector', '').strip()
    checker = request.GET.get('checker', '').strip()
    sender = request.GET.get('sender', '').strip()
    passwd = request.GET.get('mailpasswd', '').strip()
    bodymessage = request.GET.get('bodymessage', '')
    # recevier = request.GET.get('recevier', '').strip()
    # cc = request.GET.get('cc', '').strip()
    # cipher = request.GET.get('cipher', '').strip()
    cipher = 'Pixone@NetworkOP'
    recevier = "韩涛 <hantao@chinamobile.com>; 古小中 <guxiaozhong@chinamobile.com>; 李亮 <liliangit@chinamobile.com>; 周志平 <zhouzhiping@chinamobile.com>; 刘丹 <liudan@chinamobile.com>; 杨帆 <yangfanit01@chinamobile.com>; 吴长领 <wuchangling@chinamobile.com>; 鲁博 <luboit@chinamobile.com>; 李洋 <liyangit01@chinamobile.com>; 张强(IT) <zhangqiangit@chinamobile.com>; 李毅 <liyiit02@chinamobile.com>; 文静 <wenjingit02@chinamobile.com>; 尚娇龙 <shangjiaolong@chinamobile.com>; 刘天鹏 <liutianpeng@chinamobile.com>; 吴寒冰 <wuhanbing@chinamobile.com>; 徐金水 <xujinshui@chinamobile.com>; 李泱 <liyangit@chinamobile.com>; 张晓鸣 <zhangxiaomingit@chinamobile.com>;刘海峰<liuhaifeng@chinamobile.com>"
    cc = "滕滨 <tengbin@chinamobile.com>; 谢文君 <xiewenjun@chinamobile.com>; 王红 <wanghongit@chinamobile.com>"
    if not inspector:
        errors = errors + "<p>检查人为空</p>"
    if not checker:
        errors = errors + "<p>复核人为空</p>"
    if not sender:
        errors = errors + "<p>发件人为空</p>"
    elif 'error' in checkInputEmailAddress(sender):
        errors = errors + "<p>发件人邮箱地址错误</p>"
    # if not recevier:
    #     errors = errors + "<p>收件人为空</p>"
    # elif 'error' in checkInputEmailAddress(recevier):
    #     errors = errors + "<p>收件人邮箱地址错误</p>"
    # if not cc:
    #     errors = errors + "<p>抄送人为空</p>"
    # elif 'error' in checkInputEmailAddress(cc):
    #     errors = errors + "<p>抄送人邮箱地址错误</p>"
    # if not cipher:
    #     errors = errors + "<p>Cipher为空</p>"
    # elif 'error' in checkCipher(cipher):
    #     errors = errors + "<p>Cipher 错误</p>"
    if not passwd:
        errors = errors + "<p>邮箱密码为空</p>"
    elif '发件人' in errors:
        pass
    elif 'error' in checkEmail(sender, passwd):
        errors = errors + "<p>邮箱密码错误</p>"

    if errors:
        errors = '<div style="color:red">%s</div' % errors
        print(errors)
        return HttpResponse(json.dumps({'errors': errors}))
    with open('D:\\PycharmProjects\\sharezone\\config\\devicecheck', 'w+') as f:
        f.write('inspector=%s#checker=%s#sender=%s#recevier=%s#cc=%s#passwd=%s#cipher=%s#bodymessage=%s' % (
            inspector, checker, sender, recevier, cc, passwd, cipher, bodymessage))
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
        print('get %s data error %s' % (tablename, e))
        return HttpResponse({'errors': 'Get %s data encounter an error' % tablename})
    try:
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
    except:
        data = []

    for d in data:
        dataSets.append(d)

    return HttpResponse(json.dumps({'total': total, 'rows': dataSets}, cls=DatetimeEncoder))
