import IPy
import re
from datetime import datetime, date
from openpyxl import Workbook, load_workbook

access_list = ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
               'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']
access_feature = ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                  '接入IP承载网所属VPN域']
province_list = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
                 '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙', '广西', '西藏', '宁夏', '新疆', '香港', '澳门']
hq_list = ['信息港', '南方基地', '深圳', 'ucenter', '集团', '哈池', '呼池']


def isIp(address):
    try:
        IPy.IP(address)
        return True
    except Exception as e:
        return False


def cellValue(cell):
    if not cell.value:
        return ' '
    if isinstance(cell.value, str):
        return cell.value.replace('\n', ' ')
    if isinstance(cell.value, datetime):
        return cell.value.strftime('%Y%m%d')
    if isinstance(cell.value, int):
        return str(cell.value)
    return cell.value


def getHeadLine(sheet_content):
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
    # 找到首行
    for row in sheet_content.rows:
        count = 0
        cell_values1 = '|'.join([cellValue(c) for c in row])
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
        print('[ERROR] 解析Excel出错，表单【{0}】没有找到超过半数的特征值行'.format(sheet_content.title))
        return
    print('[SUCCESS] 找到有效表头的表单【{}】'.format(sheet_content.title))
    # 找到字段对应的列
    result['row_num'] = row_num
    for cell in sheet_content[row_num]:

        cv = cellValue(cell)
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
    warning += '【{}】解析失败； '.format(', '.join(unresoled))
    print('[WARNING]', warning)
    return result, warning


def extractIP(cell_content):
    '''
    提取并判断IP地址的正确性
    :param cell_content:
    :return:
    '''

    if not cell_content:
        return
    result = []
    error_msg = ''
    cell_content = cell_content.lower()
    pattern = re.compile(r'[^\d/.-]+?')

    items = re.split(pattern, cell_content)
    for item in items:
        if not item.strip(): continue
        if item == '/': continue
        if not re.match(r'^(\d{1,3}\.){3}\d{1,3}', item):
            error_msg += '[{0}]不是IP地址; '.format(item)
            continue
        if '-' in item:
            ip_list = completeIPAddress(item)
            if not ip_list:
                error_msg += '[{0}]IP无法解析; '.format(item)
                continue
            result.extend(ip_list)
        else:
            result.append(item)
    IP_list = []
    for item in result:
        if not isIp(item):
            error_msg += '[{0}]IP地址不合法; '.format(item)
            continue
        if item.startswith('255'):
            error_msg += '[{0}]为子网掩码; '.format(item)
            continue
        if item in IP_list:
            error_msg += '[{}]地址重复; '.format(item)
            continue
        IP_list.append(item)
    if not result:
        error_msg += '[{0}]没有提取到IP地址; '.format(cell_content)
    return result, error_msg


def extractProvince(cell_content):
    if not cell_content:
        return
    if not '>' in cell_content:
        return ['', '', ''], '访问方向[{0}]填写有误; '.format(cell_content)
    error_msg = ''
    access_from_checked = False
    access_to_checked = False
    cell_content = cell_content.lower()
    cell_content = re.sub(r'-{0,}>', '>', cell_content)
    items = cell_content.split('>')
    if len(items) < 2:
        return
    access_from = items[0]
    access_to = items[-1]
    if len(items) > 2:
        access_middle = items[1:-1]
    else:
        access_middle = ''
    for pl in province_list:
        if pl in access_from:
            access_from_checked = '省端'
        if pl in access_to:
            access_to_checked = '省端'
        if access_from_checked and access_to_checked:
            break
    for pl in hq_list:
        if pl in access_from:
            access_from_checked = '总部'
        if pl in access_to:
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
    return [access_from_checked, access_to_checked, access_middle], error_msg


def completeNumber(content):
    result = []
    if not '-' in content:
        return
    start = content.split('-')[0]
    end = content.split('-')[-1]
    for i in range(int(start), int(end) + 1):
        result.append(i)
    return result


def completeIPAddress(content):
    if not content:
        return
    result = []
    items = content.split('.')
    if not len(items) == 4:
        return
    if not '-' in items[-1]:
        return
    for i in completeNumber(items[-1]):
        items[-1] = str(i)
        result.append('.'.join(items))
    return result


def extractNumber(line):
    error_msg = ''
    result = []
    pattern = re.compile(r'[^\d~-]+?')
    items = pattern.split(line)
    for item in items:
        if not item: continue
        if not re.match('^\d+$', item):
            ports = completeNumber(item)
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


def extractPort(k, cell_content, tcp, udp):
    '''
    提取端口号
    :param cell_content:
    :param tcp:
    :param udp:
    :return:
    '''
    error_msg = ''

    if not cell_content.strip():
        if k.startswith('source_port'):
            return ['不限'], error_msg
        if k.endswith('to'):
            return [], '目的端口【到】内容为空; '
        return [], '目的端口【从】内容为空; '
    cell_content = cell_content.lower().replace('\n', ' ')
    if '不限' in cell_content:
        return ['不限'], error_msg
    tcp_index = -1
    udp_index = -1
    tcp_ports = []
    udp_ports = []
    if tcp and udp:
        if not ('tcp' in cell_content and 'udp' in cell_content):
            error_msg += '同时选择了TCP和UDP，但是端口{0}中未区分TCP和UDP; '.format(cell_content)
        else:
            tcp_index = cell_content.index('tcp')
            udp_index = cell_content.index('udp')
            if tcp_index > udp_index:
                tcp_ports, err_msg = extractNumber(cell_content[tcp_index + 3:])
                error_msg += err_msg
                udp_ports, err_msg = extractNumber(cell_content[:tcp_index])
                error_msg += err_msg
            else:
                tcp_ports, err_msg = extractNumber(cell_content[:udp_index])
                error_msg += err_msg
                udp_ports, err_msg = extractNumber(cell_content[udp_index + 3:])
                error_msg += err_msg
    elif tcp:
        if 'udp' in cell_content:
            error_msg += '只选择了TCP但是出现UDP，{0};'.format(cell_content)
        else:
            tcp_ports, err_msg = extractNumber(cell_content)
            error_msg += err_msg
    elif udp:
        if 'tcp' in cell_content:
            error_msg += '只选择了UDP但是出现TCP，{0};'.format(cell_content)
        else:
            udp_ports, err_msg = extractNumber(cell_content)
            error_msg += err_msg
    # print({'tcp': tcp_ports, 'udp': udp_ports}, error_msg)
    if not (tcp_ports or udp_ports):
        error_msg += '[{}]没有提取到端口信息; '.format(cell_content)
    return {'tcp': tcp_ports, 'udp': udp_ports}, error_msg


def readXlsContent(filename):
    '''

    :param filename:
    :return:
    '''
    print('处理文件：{}'.format(filename))
    items_dict = {}
    error_msgs_dict = {}
    wb = load_workbook(filename, read_only=True, data_only=True)
    sheet_list = wb.sheetnames
    for sheet_name in sheet_list:
        error_msgs = []  # 存储错误信息
        items = []  # 存储正确信息
        sheet = wb[sheet_name]
        sheet_name = sheet.title
        print('处理表单：{0}'.format(sheet_name))
        head_index, warning = getHeadLine(sheet)
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
            item_dict = {}
            error_msg = ''
            transport_protocal_tcp = sheet.cell(row=row, column=head_index['transport_protocal_tcp']).value
            transport_protocal_udp = sheet.cell(row=row, column=head_index['transport_protocal_udp']).value
            for k, v in head_index.items():
                if v < 0:
                    item_dict[k] = ' '
                    continue
                err_msg = ''
                cell_value = cellValue(sheet.cell(row=row, column=v))
                if 'IP' in k:
                    IP_list, err_msg = extractIP(cell_value)
                    item_dict[k] = IP_list
                elif '_port' in k:
                    port_dict, err_msg = extractPort(k, cell_value, transport_protocal_tcp, transport_protocal_udp)
                    item_dict[k] = port_dict
                elif k == 'direction':# 提取访问方向信息
                    acc_list, err_msg = extractProvince(cell_value)
                    item_dict[k] = acc_list
                else:
                    item_dict[k] = cell_value
                error_msg += err_msg
            # 每一行，只要出现错误信息就不添加到正确结果中
            if error_msg.strip():
                error_msg = '第[{0:^{1}d}]行数据错误：{2}'.format(row, len(str(nrows)), error_msg)
                error_msgs.append(error_msg)
                print(error_msg)
            else:
                items.append(item_dict)
                for k, v in item_dict.items():
                    print(k, v)
        items_dict[sheet_name] = items
        error_msgs_dict[sheet_name] = error_msgs

    return items_dict, error_msgs_dict

    # print(direction,source_IP,source_map_IP,source_port_from,source_port_to,dest_IP,dest_map_IP,dest_port_from,
    #       dest_port_to,transport_protocal_tcp,transport_protocal_udp,app_protocal,access_use,vpn_domain)


def complateAccessList(device, originalIP, mask, distinateIP, port):
    data = ''
    errors = {'originalIP': '', 'mask': '', 'distinateIP': '', 'port': ''}
    originalIP = originalIP.split()
    distinateIP = distinateIP.split()

    if not isIp(mask):
        errors['mask'] = mask
        return data, errors

    if len(port.split()) > 1:
        port_str = ' range '
    else:
        port_str = ' eq '

    for o in originalIP:
        if not isIp(o):
            if errors['originalIP']:
                errors['originalIP'] = errors['originalIP'] + ',' + o
            else:
                errors['originalIP'] = o
            continue
        for d in distinateIP:
            if not isIp(d):
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


#readXlsContent('C:\\Users\\Hyphen.Liu\\Desktop\\安全运营管理中心一期项目第十批IP互联工作单（态势)-用于探针策略下发.xlsx')
