from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
import json

from EasyWork.utils.json_datetime import DatetimeEncoder
from EasyWork.utils.file_operator import export2Xls
from EasyWork.utils.views_utils import *
from EasyWork.utils.database_ops import *



@login_required
def erp(request):
    tableTitle = zip(htmlTitles['erp'], htmlColums['erp'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('erp'))
    return render(request, 'pages/assets_erp.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def inventory(request):
    tableTitle = zip(htmlTitles['inventory'], htmlColums['inventory'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('inventory'))
    return render(request, 'pages/assets_inventory.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def inventoried(request):
    tableTitle = zip(htmlTitles['inventoried'], htmlColums['inventoried'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('inventoried'))
    return render(request, 'pages/assets_inventoried.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def schedual(request):
    tableTitle = zip(htmlTitles['schedual'], htmlColums['schedual'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('schedual'))
    return render(request, 'pages/assets_schedual.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def prescrap(request):
    tableTitle = zip(htmlTitles['prescrap'], htmlColums['prescrap'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('prescrap'))
    return render(request, 'pages/assets_prescrap.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def scrap(request):
    tableTitle = zip(htmlTitles['erp'], htmlColums['erp'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('scrap'))
    return render(request, 'pages/assets_scrap.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def statistic(request):
    return render(request, 'pages/assets_statistic.html')


@login_required
def scraped(request):
    tableTitle = zip(htmlTitles['scraped'], htmlColums['scraped'])
    batchQueryStatus = cache.get('batchQuery{}Status'.format('scraped'))
    return render(request, 'pages/assets_scraped.html', {'titles': tableTitle, 'querysuccess': batchQueryStatus})


@login_required
def dataimport(request):
    return render(request, 'pages/assets_dataimport.html')


@login_required
def listpage(request, tablename):
    dataSets = []
    limit = 10
    offset = 0
    if request.method == 'GET':
        limit = request.GET.get('limit')
        offset = request.GET.get('offset')

    if tablename == 'scrap':  # 只从ERP提取可报废资产信息
        tablename = 'erp'
        dataList, queryStr = intervalQuery(request)
    else:
        dataList, queryStr = simpleQuery(request, tablename)

    cache.set('export{}2XlsContent'.format(tablename), export2Xls('assets',dataList, tablename), 60)
    cache.set('export{}2XlsName'.format(tablename), tablename + '-' + queryStr, 60)

    total = dataList.count()
    try:
        paginator = Paginator(dataList, limit)
    except Exception:
        print('get {} data error'.format(tablename))
        return HttpResponse({'errors': 'Get {} data encounter an error'.format(tablename)})
    try:
        page = int(int(offset) / int(limit) + 1)
        data = paginator.page(page)
    except:
        data = []

    for d in data:
        dataSets.append(d)

    return HttpResponse(json.dumps({'total': total, 'rows': dataSets}, cls=DatetimeEncoder))


@login_required
def inventoring(request):
    default = {}
    if request.method == 'GET':
        assetLabel = request.GET.get('asset_label')
        address = request.GET.get('address')
        if assetLabel.strip():
            item = getExactlySingle('erp', 'asset_label', assetLabel).values()
            if item:
                item = item[0]

                return HttpResponse(json.dumps(item, cls=DatetimeEncoder))
        return HttpResponse(json.dumps(default))
    elif request.method == 'POST':
        assetLabel = request.POST.get('asset_label')
        address = request.POST.get('address')
        asset_model = request.POST.get('asset_model')
        asset_manufactor = request.POST.get('asset_manufactor')
        print(assetLabel, address, asset_model, asset_manufactor)
        return HttpResponse(json.dumps(default))


@login_required
def updateErp(request):
    error = ''
    if request.is_ajax():
        try:
            updateERPDepreciateDate()
            success = 'update success'
        except Exception as e:
            error = 'update erp deprecate failed!'
            success = ''
            print(error)
        return HttpResponse(json.dumps({'error': error, 'success': success}))
