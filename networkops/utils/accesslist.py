import os
import IPy
import re
from datetime import datetime, date
from django.core.cache import cache
from openpyxl import Workbook, load_workbook

access_list = ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
               'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']
access_feature = ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                  '接入IP承载网所属VPN域']
province_list = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
                 '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
hq_list = ['信息港', '南方基地', '深圳', 'ucenter', '集团', '哈池', '呼池']


def _isIp(address):
    try:
        IPy.IP(address)
        return True
    except Exception as e:
        return False


def _cellValue(cell):
    if not cell.value:
        return ''
    if isinstance(cell.value, str):
        return cell.value.replace('\n', ' ')
    if isinstance(cell.value, datetime):
        return cell.value.strftime('%Y%m%d')
    if isinstance(cell.value, int):
        return str(cell.value)
    return cell.value


def _getHeadLine(sheet_content):
    '''
    返回字段所在的行/列号，没有找到的字段列号为-1
    :param sheet_content:
    :return: result{access_list:column_num}
    '''

    result = {}
    col_nums = []
    warning = ''
    for sl in access_list:
        result[sl] = -1
    row_num = -1
    m_cells = sheet_content.merged_cells  # 获取所有的合并单元格，以供后面判断
    print(m_cells)
    # 找到首行
    for row in sheet_content.rows:
        count = 0
        cell_values1 = '|'.join([_cellValue(c) for c in row])
        cell_values = cell_values1.replace('\n', '').strip(' |')
        if (len(cell_values1) - len(cell_values)) > 20:
            warning = '表格[{}]存在大量无效空列，影响程序运行速度； '.format(sheet_content.title)
            print(warning)
        # result['ncols'] = len(cell_values.split('|')) # 有效列数，有的表格可能有好多空列，影响到运行速度
        for af in access_feature:
            if af in cell_values: count += 1
        if count > len(access_feature) / 2:
            row_num = row[1].row
            break
    if row_num < 0:
        print('[ERROR] 解析Excel出错，表单【{0}】没有找到超过半数的特征值行; '.format(sheet_content.title))
        return {}, warning
    print('[SUCCESS] 找到有效表头的表单【{}】'.format(sheet_content.title))
    # 找到字段对应的列
    result['row_num'] = row_num
    for cell in sheet_content[row_num]:
        print(cell.column)
        print(cell.row)
        cv = _cellValue(cell)
        cv = re.sub(r'\s', '', cv)
        if not isinstance(cv, str) or not cv:
            # print('【ERROR】解析Excel第{0}行出错，存在单元格为空'.format(row_num))
            continue
        for af in access_feature:
            key = access_list[access_feature.index(af)]  # 根据特征值找到对应的存储字典key值
            if af in cv and (result[key] < 0) and (cell.column not in col_nums):
                if af in ['源端口', '目的端口', '传输层协议']:
                    first_col = sheet_content.cell(row=cell.row + 1, column=cell.column).value
                    if not af == '传输层协议':
                        if first_col == '从':
                            s = cell.column
                            d = cell.column + 1
                        else:
                            s = cell.column + 1
                            d = cell.column
                        if af == '源端口':
                            result['source_port_from'] = s
                            result['source_port_to'] = d
                        else:
                            result['dest_port_from'] = s
                            result['dest_port_to'] = d
                    else:
                        if first_col == 'tcp':
                            t = cell.column
                            u = cell.column + 1
                        else:
                            t = cell.column + 1
                            u = cell.column
                        result['transport_protocal_tcp'] = t
                        result['transport_protocal_udp'] = u
                else:
                    result[key] = cell.column
                col_nums.append(cell.column)
            elif ('映射IP' in af) and ('映射IP' in cv) and (cell.column not in col_nums):
                if '源地址' in cv:
                    result['source_map_IP'] = cell.column
                    col_nums.append(cell.column)
                elif '目的地址' in cv:
                    result['dest_map_IP'] = cell.column
                    col_nums.append(cell.column)
                else:
                    warning += '映射地址表头[{}]解析错误; '.format(cv)
    for i in ['transport_protocal', 'source_port', 'dest_port']:
        result.pop(i)
    unresoled = []
    for k, v in result.items():
        if v < 0:
            unresoled.append(access_feature[access_list.index(k)])
    if unresoled:
        warning += '【{}】解析失败； '.format(', '.join(unresoled))
    print('[WARNING]', warning)
    return result, warning


def _extractIP(cell_content, column_name):
    '''
    提取并判断IP地址的正确性
    :param cell_content:
    :return:[ip1,ip2]
    '''

    if not cell_content:
        return [], '<u><b>{}</b></u>单元格为空; '.format(column_name)
    result = []
    error_msg = []
    cell_content = cell_content.lower()
    pattern = re.compile(r'[^\d/.~-]+?')

    items = re.split(pattern, cell_content)
    for item in items:
        if not item.strip(): continue
        if item == '/': continue
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}', item):
            e_msg = '[{0}]不是IP地址; '.format(item)
            if not e_msg in error_msg:
                error_msg.append(e_msg)
            continue
        if '-' in item or '~' in item:
            ip_list = _completeIPAddress(item)
            if not ip_list:
                e_msg = '[{0}]IP无法解析; '.format(item)
                if not e_msg in error_msg:
                    error_msg.append(e_msg)
                continue
            result.extend(ip_list)
        else:
            result.append(item)
    IP_list = []
    for item in result:
        if not _isIp(item):
            e_msg = '[{0}]IP地址不合法; '.format(item)
            if not e_msg in error_msg:
                error_msg.append(e_msg)
            continue
        if item.startswith('255'):
            e_msg = '[{0}]为子网掩码; '.format(item)
            if not e_msg in error_msg:
                error_msg.append(e_msg)
            continue
        if item in IP_list:
            e_msg = '[{}]地址重复; '.format(item)
            if not e_msg in error_msg:
                error_msg.append(e_msg)
            continue
        IP_list.append(item)
    if not result:
        e_msg = '<u><b>{}</b></u>没有提取到IP地址; '.format(column_name)
        if not e_msg in error_msg:
            error_msg.append(e_msg)
    return sorted(result), ''.join(error_msg)


def _extractProvince(cell_content, column_name):
    '''
    提取策略访问方向
    :param cell_content:
    :return: [源，目的，[中间]]
    '''
    if not cell_content:
        return [], '<u><b>{}</b></u>单元格为空; '.format(column_name)
    if not '>' in cell_content:
        return ['', '', ''], '<u><b>{}</b></u>[{}]填写有误; '.format(column_name, cell_content)
    error_msg = ''
    access_from_checked = False
    access_to_checked = False
    cell_content = cell_content.lower()
    cell_content = re.sub(r'[—-]{0,}>', '>', cell_content)
    items = cell_content.split('>')
    if len(items) < 2:
        return [], '<u><b>{}</b></u>未使用“->”符号区分访问方向; '.format(column_name)
    access_from = items[0]
    access_to = items[-1]
    for pl in province_list:
        if pl in access_from:
            items[0] = pl
            access_from_checked = '省端'
        if pl in access_to:
            items[-1] = pl
            access_to_checked = '省端'
        if access_from_checked and access_to_checked:
            break
    for pl in hq_list:
        if pl in access_from:
            items[0] = pl
            access_from_checked = '总部'
        if pl in access_to:
            items[-1] = pl
            access_to_checked = '总部'
        if access_from_checked and access_to_checked:
            break
    if not access_from_checked:
        error_msg += '源位置信息[{0}]不在省或总部列表中; '.format(access_from)
    if not access_to_checked:
        error_msg += '目的位置信息[{0}]不在省或总部列表中; '.format(access_to)
        print(error_msg)
    # print(access_from_checked, '|'.join(access_middle), access_to_checked)
    if not (access_from_checked and access_to_checked):
        error_msg += '[{0}]提取访问方向错误; '.format(cell_content)
    route = '->'.join(items)
    return route.upper(), error_msg


def _completeNumber(content):
    '''
    补充连续的数字
    :param content:
    :return:
    '''
    result = []
    if '-' in content:
        start = content.split('-')[0]
        end = content.split('-')[-1]
    elif '~' in content:
        start = content.split('~')[0]
        end = content.split('~')[-1]
    else:
        return
    for i in range(int(start), int(end) + 1):
        result.append(i)
    return result


def _completeIPAddress(content):
    if not content:
        return
    result = []
    items = content.split('.')
    if not len(items) == 4:
        return
    if not ('-' in items[-1] or '~' in items[-1]):
        return
    for i in _completeNumber(items[-1]):
        items[-1] = str(i)
        result.append('.'.join(items))
    return result


def _extractNumber(line):
    error_msg = ''
    result = []
    pattern = re.compile(r'[^\d~-]+?')
    items = pattern.split(line)
    for item in items:
        if not item: continue
        if not re.match('^\d+$', item):
            ports = _completeNumber(item)
            if not ports:
                error_msg += '[{0}]端口解析错误; '.format(item)
                continue
            for p in ports:
                if p > 65535 or p < 1:
                    error_msg += '[{0}]端口非法; '.format(item)
                    continue
            result.extend(ports)
        elif int(item) > 65535 or int(item) < 1:
            error_msg += '[{0}]端口非法; '.format(item)
            continue
        else:
            result.append(int(item))
    return result, error_msg


def _extractPort(k, cell_content, tcp, udp):
    '''
    提取端口号
    :param cell_content:
    :param tcp:
    :param udp:
    :return: {'tcp':[],'udp':[]}
    '''
    error_msg = ''
    # 单元格内容为空
    if not cell_content.strip():
        if k.startswith('source_port'):
            return ['不限'], error_msg
        return [], error_msg
    # 单元格内容不为空
    cell_content = cell_content.lower().replace('\n', ' ')
    if '不限' in cell_content:
        return ['不限'], error_msg
    tcp_ports = []
    udp_ports = []
    if tcp and udp:
        if not ('tcp' in cell_content and 'udp' in cell_content):
            error_msg += '同时选择了TCP和UDP，但是端口{0}中未区分TCP和UDP; '.format(cell_content)
        else:
            tcp_index = cell_content.index('tcp')
            udp_index = cell_content.index('udp')
            if tcp_index > udp_index:
                tcp_ports, err_msg = _extractNumber(cell_content[tcp_index + 3:])
                error_msg += err_msg
                udp_ports, err_msg = _extractNumber(cell_content[:tcp_index])
                error_msg += err_msg
            else:
                tcp_ports, err_msg = _extractNumber(cell_content[:udp_index])
                error_msg += err_msg
                udp_ports, err_msg = _extractNumber(cell_content[udp_index + 3:])
                error_msg += err_msg
    elif tcp:
        if 'udp' in cell_content:
            error_msg += '只选择了TCP但是出现UDP端口; '
        else:
            tcp_ports, err_msg = _extractNumber(cell_content)
            error_msg += err_msg
    elif udp:
        if 'tcp' in cell_content:
            error_msg += '只选择了UDP但是出现TCP端口; '
        else:
            udp_ports, err_msg = _extractNumber(cell_content)
            error_msg += err_msg
    else:
        error_msg += '未选择传输协议; '
    # print({'tcp': tcp_ports, 'udp': udp_ports}, error_msg)
    if not re.findall(r'\d+', cell_content):
        error_msg += '[{}]没有提取到端口信息; '.format(cell_content)
    return {'tcp': sorted(tcp_ports), 'udp': sorted(udp_ports)}, error_msg


def _completePortNumber(port_from, port_to):
    '''
    补全端口“从”-“到”之间的连续数字，确保tcp端口已经按升序排序
    :param port_from: {'tcp': 'xx\nxx', 'udp': 'xx\nxx'}
    :param port_to: {'tcp': 'xx\nxx', 'udp': 'xx\nxx'}
    :return: {'tcp': 'xx\nxx', 'udp': 'xx\nxx'}
    '''
    f_tcp = port_from['tcp']
    f_udp = port_from['udp']
    t_tcp = port_to['tcp']
    t_udp = port_to['udp']
    result = {'tcp': '', 'udp': ''}
    error_msg = ''
    if not ((f_tcp and t_tcp) or (f_udp and t_udp)):
        error_msg += '端口【从】和【到】协议不相同/'
    elif f_tcp and t_tcp:
        ports, err_msg = _checkPort(f_tcp, t_tcp)
        if err_msg:
            error_msg += err_msg
        else:
            result['tcp'] = '\n'.join(str(i) for i in ports)
    elif f_udp and t_udp:
        ports, err_msg = _checkPort(f_tcp, t_tcp)
        if err_msg:
            error_msg += err_msg
        else:
            result['udp'] = '\n'.join(str(i) for i in ports)
    if error_msg:
        error_msg = error_msg.strip('/') + '; '
    return result, error_msg


def _checkPort(f_ports, t_ports):
    '''

    :param f_ports:
    :param t_ports:
    :return:
    '''
    ports = []
    error_msg = ''
    if not len(f_ports.split('\n')) == len(t_ports.split('\n')):
        error_msg += '端口【从】和【到】端口号数量不同;'
        return ports, error_msg

    f_ports = f_ports.split('\n')
    t_ports = t_ports.split('\n')
    for i in range(len(f_ports)):
        if f_ports[i] > t_ports[i]:
            error_msg += '端口【从】大于【到】端口号数值/'
            break
        elif (i + 1) > len(f_ports):
            if t_ports[i] > f_ports[i + 1]:
                error_msg += '端口【从】和【到】端口号数值范围存在重叠/'
                break
    if error_msg:
        return ports, error_msg

    items = zip(f_ports, t_ports)
    for s, e in items:
        if s > e:
            error_msg += '端口【从】大于【到】端口号数值/'
        else:
            ports.extend(_completeNumber(s + '-' + e))
    return ports, error_msg


def _sortItem(item_dict):
    '''
    将每一行的字典值转化为列表值，以便存入到数据库中。前提是前面的已经将错误信息处理了
    :param item_dict:
    :return:['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
            'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']
    '''
    error_msg = ''
    items = []
    # 处理源端口信息
    s_port_from = item_dict['source_port_from']
    s_port_to = item_dict['source_port_to']
    if s_port_from and s_port_to:
        if s_port_from == s_port_to:
            item_dict['source_port'] = s_port_from
        else:
            ports, err_msg = _completePortNumber(s_port_from, s_port_to)
            if err_msg:
                error_msg += err_msg
            else:
                item_dict['source_port'] = ports
    elif not (s_port_from or s_port_to):
        item_dict['source_port'] = '不限'
    elif s_port_from:
        item_dict['source_port'] = s_port_from
    else:
        item_dict['source_port'] = s_port_to
    # 处理目的端口信息
    d_port_from = item_dict['dest_port_from']
    d_port_to = item_dict['dest_port_to']
    if d_port_from and d_port_to:
        if d_port_from == d_port_to:
            item_dict['dest_port'] = d_port_from
        else:
            ports, err_msg = _completePortNumber(d_port_from, d_port_to)
            if err_msg:
                error_msg += err_msg
            else:
                item_dict['dest_port'] = ports
    elif not (d_port_from or d_port_to):
        error_msg = '没有指定目的端口号; '
    elif d_port_from:
        item_dict['dest_port'] = d_port_from
    else:
        item_dict['dest_port'] = d_port_to
    # 前面出现错误信息则终止
    if error_msg: return items, error_msg
    # 拆分同时含有TCP和UDP协议的端口为2条信息
    if item_dict['dest_port']['tcp']:
        items.append(
            [item_dict['direction'], item_dict['source_IP'], item_dict['source_map_IP'], item_dict['source_port'],
             item_dict['dest_IP'], item_dict['dest_map_IP'], item_dict['dest_port']['tcp'], 'tcp',
             item_dict['app_protocal'], item_dict['access_use'], item_dict['vpn_domain']])
    if item_dict['dest_port']['udp']:
        items.append(
            [item_dict['direction'], item_dict['source_IP'], item_dict['source_map_IP'], item_dict['source_port'],
             item_dict['dest_IP'], item_dict['dest_map_IP'], item_dict['dest_port']['udp'], 'udp',
             item_dict['app_protocal'], item_dict['access_use'], item_dict['vpn_domain']])

    return items, error_msg


def readXlsContent(tableName, filename):
    '''
    读取excel表格内容，获取网络策略开通单的表头，提取表头对应列的数据
    :param filename:
    :return:data=[['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
                    'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']......],
            msg_dict={'error':'','warning':''} # HTML格式的字符串
    '''
    print('处理文件：{}'.format(filename))
    data = []
    message = ''
    warning_msgs = []
    error_msgs = []
    wb = load_workbook(filename, data_only=True)
    sheet_list = wb.sheetnames
    for sheet_name in sheet_list:
        errors = []  # 存储检查本表单发现的错误信息
        sheet = wb[sheet_name]
        sheet_name = sheet.title
        print('处理表单：{0}'.format(sheet_name))
        head_index, warning = _getHeadLine(sheet)
        if not head_index:
            continue
        # print(head_index)
        nrows = sheet.max_row
        start_row = head_index['row_num'] + 1
        head_index.pop('row_num')
        if nrows < start_row + 1:
            print('{0}表格内容为空，请检查！'.format(sheet.title))
            return
        for row in range(start_row + 1, nrows + 1):
            if not ''.join([_cellValue(c) for c in sheet[row]]): continue
            item_dict = {}  # 记录每一列的信息
            error_msg = []  # 记录每一行的错误信息
            transport_protocal_tcp = sheet.cell(row=row, column=head_index['transport_protocal_tcp']).value
            transport_protocal_udp = sheet.cell(row=row, column=head_index['transport_protocal_udp']).value
            for k, v in head_index.items():
                if v < 0:
                    item_dict[k] = ''
                    continue
                err_msg = ''
                cell_value = _cellValue(sheet.cell(row=row, column=v))
                if 'IP' in k:
                    IP_list, err_msg = _extractIP(cell_value, access_feature[access_list.index(k)])
                    item_dict[k] = '\n'.join(IP_list)
                elif '_port' in k:
                    port_dict, err_msg = _extractPort(k, cell_value, transport_protocal_tcp, transport_protocal_udp)
                    if isinstance(port_dict, dict):
                        for i, j in port_dict.items():
                            port_dict[i] = '\n'.join(str(n) for n in j)
                        item_dict[k] = port_dict
                    else:
                        item_dict[k] = '\n'.join(str(i) for i in port_dict)
                elif k == 'direction':  # 提取访问方向信息
                    acc_list, err_msg = _extractProvince(cell_value, access_feature[access_list.index(k)])
                    item_dict[k] = acc_list
                else:
                    item_dict[k] = cell_value
                # 去除重复的错误
                if not (err_msg.strip() in error_msg):
                    error_msg.append(err_msg.strip())
            error_msg = ''.join(error_msg)
            # 处理每一列的信息，将字典值转化为列表值，处理端口信息
            item_list, err_msg = _sortItem(item_dict)
            error_msg += err_msg
            # 每一行，只要出现错误信息就不添加到最终结果中
            if error_msg.strip():
                error_msg = '第[{0:^{1}d}]行数据错误：{2}'.format(row, len(str(nrows)), error_msg)
                errors.append(error_msg)
                # print(error_msg)
            else:
                for il in item_list:
                    data.append(il)
        if warning:  # 合并告警信息
            warning_msgs.append('表单<b>《{}》</b>存在的告警信息：'.format(sheet_name))
            warning_msgs.append(warning)
        if errors:  # 合并错误信息
            error_msgs.append('表单<b>《{}》</b>存在的错误信息：'.format(sheet_name))
            error_msgs.extend(errors)
    # print(data, {'warning': warning_msgs, 'errors': error_msgs})
    if warning_msgs:
        message += '<div style="background:#FF0">{}</div>'.format(
            ''.join(['<p>{}</p>'.format(i) for i in warning_msgs]))
    if error_msgs:
        message += '<div style="color:#F00">{}</div>'.format(''.join(['<p>{}</p>'.format(i) for i in error_msgs]))
    # 写入原始数据到文件中，并在redis中提供下载刚刚生成的文件
    # _writeContent(tableName, filename, data)
    return data, message


def _writeContent(tableName, filename, data):
    '''
    生成网络策略开通文件
    :param tableName:
    :param filename:
    :param data:
    :return:
    '''
    file_pre, ext = os.path.splitext(filename)
    filename = '{0}{1}{2}'.format(file_pre[:-20], file_pre[-20:-9], ext)  # 去掉自动添加上去的时间戳
    file_item = filename.split(os.sep)
    file_item[-2] = 'download'
    filename = os.sep.join((file_item))
    if os.path.exists(filename): os.remove(filename)  # 删除已经存在的文件
    wb = Workbook()
    for k, v in data.items():
        ws = wb.create_sheet(k, 0)
        for row in range(len(v)):
            for col in range(len(v[row])):
                ws.cell(row=row + 1, column=col + 1, value=v[row][col])  # cell 起始位置必须是1而非0
    wb.save(filename)
    wb.close()
    cache.set('download{0}{1}file'.format('dailywork', tableName), filename, 1 * 60)


def complateAccessList(device, originalIP, mask, distinateIP, port):
    data = ''
    errors = {'originalIP': '', 'mask': '', 'distinateIP': '', 'port': ''}
    originalIP = originalIP.split()
    distinateIP = distinateIP.split()

    if not _isIp(mask):
        errors['mask'] = mask
        return data, errors

    if len(port.split()) > 1:
        port_str = ' range '
    else:
        port_str = ' eq '

    for o in originalIP:
        if not _isIp(o):
            if errors['originalIP']:
                errors['originalIP'] = errors['originalIP'] + ',' + o
            else:
                errors['originalIP'] = o
            continue
        for d in distinateIP:
            if not _isIp(d):
                if errors['distinateIP']:
                    errors['distinateIP'] = errors['originalIP'] + ',' + d
                else:
                    errors['distinateIP'] = d
                continue
            if device == 'CISCO':
                accesslist_str = 'access-list outside extended permit tcp ' + str(o) + ' ' + str(mask) + ' host ' + str(
                    d) + port_str + ' ' + str(port)
            elif device in ['H3C', 'huawei']:
                accesslist_str = 'rule permit tcp source ' + str(o) + ' ' + str(mask) + ' destination ' + str(
                    d) + port_str + ' ' + str(port)
            else:
                accesslist_str = '请选择厂商'
            data = data + '<p>' + accesslist_str + '</p>'
    return data, errors
