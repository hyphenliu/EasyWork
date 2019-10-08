import time, os, re, sqlite3
from collections import defaultdict

from .database_ops import *
from .data_struct import *


class FeiXin:
    def __init__(self):
        '''
        '317817963':'IT公司网络安全演练',
        '318028642':'HW-封堵群',
        '317956808':'深圳IT安全保障',
        '317860920':'基础防护群',
        '''
        DBPATH = 'D:\\Documents\\feixin\\479286517\\sqlite\\15019289058.db'
        self.tmp_file = 'D:\\PycharmProjects\\sharezone\\config\\feixin.tmp'

        mydb = sqlite3.connect(DBPATH)
        self.cursor = mydb.cursor()
        with  open(self.tmp_file, 'r') as f:
            flcontent = f.readlines()
        if not flcontent:
            print('[ERROR] open file %s error' % self.tmp_file)
            return
        # {'分类':[群ID, 来源, 特征值, 起始时间, 结束时间]}
        self.keywords_dict = {
            'fengdu': ['318028642', '安全管理中心值班', 'FD-%%-%%请相关部门'],
            'yifengdu': ['318028642', '基础平台', 'FD-%%-%%封堵'],
            'jiefeng': ['318028642', '安全管理中心值班', '解封-%%-%%请解封'],
            'yijiefeng': ['318028642', '基础平台', '解封-%%-%%解封'],
            'paicha': ['317817963', '安全管理中心值班', 'PC-%%-%%请相关部门'],
            'jichufd': ['317860920', '深基', 'FD-%%封堵'],
            'jichujf': ['317860920', '深基', '解封-%%-'],
            'baozhang': ['317956808', '', '是否封堵']
        }
        for fl in flcontent:
            items = fl.strip().split('|')
            self.keywords_dict[items[0]].extend([int(items[1]), int(items[2])])
        # 依次获取4个群中的8类未读消息的时间戳
        sql = 'select t.userid, t.timeTamp from nRecent t'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for r in result:
            for k, v in self.keywords_dict.items():
                if r[0] == v[0]:
                    v[-1] = r[1]

    def getUnreadMsg(self, words):
        '''
        读取飞信未读消息
        :param groupId: 群ID
        :param nickName: 发消息的人
        :param contentBuffer: 消息内容
        :return: 返回数据
        '''
        groupId, nickName, contentBuffer, start, end = words
        table_name = 'nMessageGroup_%s' % groupId
        info_sql = "select t.timeStamp,t.fromNickname,t.contentBuffer from %s t where t.timeStamp > %s and t.timeStamp <= %s and t.fromNickname like '%%%s%%' and t.contentBuffer like '%%%s%%' and t.contentType='text/plain'" % (
            table_name, start, end, nickName, contentBuffer)
        self.cursor.execute(info_sql)
        info_data = self.cursor.fetchall()

        return info_data

    def writeTemfile(self):
        '''
        更新时间戳临时文档
        :return:
        '''
        flcontent = ''
        for k, v in self.keywords_dict.items():
            flcontent += '|'.join([k, str(v[-2]), str(v[-1])]) + '\n'
        with open(self.tmp_file, 'w') as f:
            f.write(flcontent)

    def extractAll(self):
        '''
        data:{'fengdu':[],'jiefeng':[]...}
        :return:
        '''
        print('[INFO] Extracting information from feixin.[%s]' % time.ctime())
        result = defaultdict(list)
        for k, v in self.keywords_dict.items():
            # print('{:=^60}'.format(k))
            if v[-1] == v[-2]: continue
            data = self.getUnreadMsg(v)
            # for d in data[-15:]:
            # print(d)
            self.keywords_dict[k][-2] = v[-1]  # 更新结束时间戳
            result[k] = data
        self.writeTemfile()
        time.sleep(3)
        return result


def feixinInfo2DB():
    '''
    格式化提出来的数据
    :return: {
                'fengdu':   [{'serial_number':'','ip_list':'','reason':'','time':'','resource':'','income_time':''},...],
                'yifengdu': [{'serial_number':'','income_time':'','resource':'','outcome':''},...],
                'jiefeng':  [{'serial_number':'','ip_list':'','income_time':'','resource':''},...],
                'yijiefeng':[{'serial_number':'','income_time':'','resource':'','outcome':''},...],
                'paicha':   [{'serial_number':'','reason':'','ip_attack':'','ip_attacked':'','location':'','means':'','guard':'','income_time':'','resource':''},...],
                'jichufd':  [{'serial_number':'','income_time':'','resource':'','outcome':'','':'','':''},...],
                'jichujf':  [{'serial_number':'','income_time':'','resource':'','outcome':'','':'','':''},...],
                'baozhang': [{'reason':'','ip_source':'','ip_dest':'','income_time':'','resource':'','level':''},...]
            }
    '''

    result_dict = defaultdict(list)
    fx = FeiXin()
    data_dict = fx.extractAll()
    if data_dict:
        print('[INFO] Serializing information from feixin')
    for k, v in data_dict.items():
        for d in v:
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d[0] / 1000))
            resource = d[1]
            contents = d[2].strip().replace('\n', ' ')
            if k == 'fengdu':
                items = fengduExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['fengdu'].extend(items)
            if k == 'yifengdu':
                items = yifengduExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['yifengdu'].extend(items)
            if k == 'jiefeng':
                items = jiefengExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['jiefeng'].extend(items)
            if k == 'yijiefeng':
                items = yijiefengExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['yijiefeng'].extend(items)
            if k == 'paicha':
                items = paichaExtract(contents, time_str, resource)
                if not items:
                    items = paichaExtract2(contents, time_str, resource)
                    if not items:
                        continue
                result_dict['paicha'].extend(items)
            if k == 'jichufd':
                items = jichufdExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['jichufd'].extend(items)
            if k == 'jichujf':
                items = jichujfExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['jichujf'].extend(items)
            if k == 'baozhang':
                items = baozhangExtract(contents, time_str, resource)
                if not items:
                    continue
                result_dict['baozhang'].extend(items)
    if result_dict['baozhang']:
        playMusic(result_dict['baozhang'])
    if result_dict['paicha']:
        playMusic(result_dict['paicha'])
    return result_dict


def baozhangExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    baozhangPattern = re.compile('(?P<reason>.+?)源(?P<ip_source>.*?)目(?P<ip_dest>.*?)是否封堵',
                                 re.I)
    items = re.finditer(baozhangPattern, contents)
    for it in items:
        item_dict = it.groupdict()
        ip_source = ipExtract(item_dict['ip_source'])
        if not ip_source:
            print('[Not normal][baozhang][source IP error] %s' % contents)
        item_dict['ip_source'] = ip_source
        ip_dest = ipExtract(item_dict['ip_dest'])
        if not ip_dest:
            print('[Not normal][baozhang][destination IP error] %s' % contents)
        item_dict['ip_dest'] = ip_dest
        item_dict['income_time'] = time_str
        item_dict['resource'] = resource
        if '高级事件' in item_dict['reason']:
            item_dict['level'] = '高级事件告警'
        elif '中级事件' in item_dict['reason']:
            item_dict['level'] = '中级事件告警'
        else:
            item_dict['level'] = '未提取到'
        result.append(item_dict)
    if not result:
        print('[Not normal][baozhang] %s' % contents)
        item_dict = {'reason': contents, 'ip_source': ' ', 'ip_dest': ' ', 'income_time': time_str,
                     'resource': resource}
        result.append(item_dict)
    return result


def jichujfExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    jichujfPattern = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)完成', re.I)
    jichujfPattern1 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)解封过', re.I)
    jichujfPattern2 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)已解封', re.I)
    jichujfPattern3 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)没封', re.I)
    jichujfPattern4 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)解封成功', re.I)
    jichujfPattern5 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)未做封堵', re.I)
    jichujfPattern6 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)未封堵', re.I)
    jichujfPattern8 = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)没有封堵过', re.I)

    wc_index = contents.find('完成')
    jfg_index = contents.find('解封过')
    yjf_index = contents.find('已解封')
    mf_index = contents.find('没封')
    cg_index = contents.find('解封成功')
    wf_index = contents.find('未做封堵')
    wfd_index = contents.find('未封堵')
    myfdg_index = contents.find('没有封堵过')
    index_dict = {
        'wancheng': [wc_index, wc_index + 2, '解封完成', jichujfPattern],
        'jiefengguo': [jfg_index, jfg_index + 3, '解封过', jichujfPattern1],
        'yijiefeng': [yjf_index, yjf_index + 3, '已解封', jichujfPattern2],
        'meifeng': [mf_index, mf_index + 2, '没封', jichujfPattern3],
        'chenggong': [cg_index, cg_index + 4, '解封成功', jichujfPattern4],
        'weizuofengdu': [wf_index, wf_index + 4, '未做封堵', jichujfPattern5],
        'weifengdu': [wfd_index, wfd_index + 3, '未封堵', jichujfPattern6],
        'meifengduguo': [myfdg_index, myfdg_index + 5, '没有封堵过', jichujfPattern8],
    }
    index_dict = sorted(index_dict.items(), key=lambda x: x[1][0])
    content_index = 0  # 切分content为不同的字符串
    for k, v in index_dict:
        if v[0] == -1:
            continue
        content = contents[content_index:v[1]]
        content_index = v[1]
        if len(content) < 3:
            continue
        extract_list = jichujfSubExtract(content, v[-1])
        if not extract_list:
            print('[Not normal][jichujf][sub extract] %s' % content)
            continue
        for el in extract_list:
            item_dict = {'serial_number': el, 'income_time': time_str, 'resource': resource, 'outcome': v[2]}
            if item_dict not in result:
                result.append(item_dict)
    if not result:
        print('[Not normal][jichujf] %s' % contents)
        result.append({'serial_number': contents, 'income_time': time_str, 'resource': resource, 'outcome': ' '})
    return result


def jichujfSubExtract(contents, jichujfPattern):
    sub_pattern = re.compile('(?P<serial_number>解封-\d+-\d+)', re.I)
    serialnumber_str = jichujfPattern.match(contents)
    if not serialnumber_str:
        return False
    serialnumbers = re.finditer(sub_pattern, serialnumber_str.groupdict()['serial_number'])
    items = []
    for it in serialnumbers:  # 这里可以确定匹配成功
        item = it.groupdict()['serial_number']
        items.append(item)
    return compeleteContinueNumber(contents, items)


def jichufdExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    jichufdPattern = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)(?P<outcome>完成)', re.I)
    jichufdPattern2 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)(?P<outcome>ipv6)', re.I)
    jichufdPattern4 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)(?P<outcome>封堵过)', re.I)
    jichufdPattern5 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)(?P<outcome>已封堵)', re.I)
    jichufdPattern7 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)(?P<outcome>封堵成功)', re.I)

    wc_index = contents.find('完成')
    v6_index = contents.find('ipv6')
    fg_index = contents.find('封堵过')
    yfd_index = contents.find('已封堵')
    cg_index = contents.find('封堵成功')
    index_dict = {
        'wancheng': [wc_index, wc_index + 2, '封堵完成', jichufdPattern],
        'ipv6': [v6_index, v6_index + 4, '不支持ipv6', jichufdPattern2],
        'fengguo': [fg_index, fg_index + 3, '封堵过', jichufdPattern4],
        'yifengdu': [yfd_index, yfd_index + 3, '已封堵', jichufdPattern5],
        'chenggong': [cg_index, cg_index + 4, '封堵成功', jichufdPattern7],

    }
    index_dict = sorted(index_dict.items(), key=lambda x: x[1][0])
    content_index = 0  # 切分content为不同的字符串
    for k, v in index_dict:
        if v[0] == -1:
            continue
        content = contents[content_index:v[1]]
        content_index = v[1]
        extract_list = jichufdSubExtract(content, v[-1])
        if not extract_list:
            print('[Not normal][jichufd][sub extract] %s' % content)
            continue
        for el in extract_list:
            item_dict = {'serial_number': el, 'income_time': time_str, 'resource': resource, 'outcome': v[2]}
            if item_dict not in result:
                result.append(item_dict)
    if not result:
        print('[Not normal][jichufd] %s' % contents)
        index = contents.find('FD-')
        if index > 0:
            result.append(
                {'serial_number': contents[index:], 'income_time': time_str, 'resource': resource, 'outcome': ' '})
    return result


def jichufdSubExtract(contents, jichufdPattern):
    sub_pattern = re.compile('(?P<serial_number>FD-\d+-\d+)', re.I)
    serialnumber_str = jichufdPattern.match(contents)
    if not serialnumber_str:
        return False
    serialnumbers = re.finditer(sub_pattern, serialnumber_str.groupdict()['serial_number'])
    items = []
    for it in serialnumbers:  # 这里可以确定匹配成功
        item = it.groupdict()['serial_number']
        items.append(item)
    return compeleteContinueNumber(contents, items)


def paichaExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    paichaPattern1 = re.compile(
        '(?P<serial_number>PC-\d+-\d+)【(?P<reason>.+?)】.+?[攻击|IP|从|到|来自].*?[:：](?P<ip_attack>.+?)[被攻|IP|对].*?[:：](?P<ip_attacked>.+?)物理.*?[:：](?P<location>.+)攻击.*?[:：](?P<means>.+?)防护.*?[:：](?P<guard>.+?$)',
        re.I)
    items = re.finditer(paichaPattern1, contents)
    for it in items:
        item_dict = it.groupdict()
        ip_attack = ipExtract(item_dict['ip_attack'])
        if not ip_attack:
            print('[Not normal][paicha][attack IP error] %s' % item_dict)
            continue
        item_dict['ip_attack'] = ip_attack
        ip_attacked = ipExtract(item_dict['ip_attacked'])
        if not ip_attacked:
            print('[Not normal][paicha][attacked IP error] %s' % item_dict)
            continue
        item_dict['ip_attacked'] = ip_attacked
        item_dict['income_time'] = time_str
        item_dict['resource'] = resource
        result.append(item_dict)
    if not result:
        print('[Not normal][paicha] %s' % contents)
    return result


def paichaExtract2(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    paichaPattern1 = re.compile('(?P<serial_number>PC-\d+-\d+)(?P<reason>.+)', re.I)
    locationPattern = re.compile('物理.*?[:：](?P<location>.{3})')
    items = re.finditer(paichaPattern1, contents)
    for it in items:
        item_dict = it.groupdict()
        if locationPattern.match(item_dict['reason']):
            item_dict['location'] = locationPattern.match(item_dict['reason'])
        else:
            item_dict['location'] = ' '
        item_dict['ip_attack'] = ' '
        item_dict['ip_attacked'] = ' '
        item_dict['guard'] = '排查'
        item_dict['means'] = ' '
        item_dict['income_time'] = time_str
        item_dict['resource'] = resource
        result.append(item_dict)
    if not result:
        print('[Not normal][paicha2] %s' % contents)
        item_dict = {'serial_number': ' ', 'reason': contents, 'ip_attack': ' ', 'ip_attacked': ' ', 'location': ' ',
                     'means': ' ', 'guard': '排查', 'result': ' ', 'income_time': time_str, 'resource': resource, }
        result.append(item_dict)
    return result


def yijiefengExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    yijifengPattern = re.compile('.*?(?P<serial_number>解封-\d+-\d+.*?)已解封', re.I)
    sub_pattern = re.compile('(?P<serial_number>解封-\d+-\d+)', re.I)
    serialnumber_str = yijifengPattern.match(contents)
    if not serialnumber_str:
        print('[Not normal][yijiefeng] %s' % contents)
        return False
    serialnumbers = re.finditer(sub_pattern, serialnumber_str.groupdict()['serial_number'])
    items = []
    for it in serialnumbers:  # 这里可以确定匹配成功
        item = it.groupdict()['serial_number']
        items.append(item)
    serial_list = compeleteContinueNumber(contents, items)
    for sl in serial_list:
        result.append({'serial_number': sl, 'outcome_time': time_str, 'excutor': resource, 'outcome': '已解封'})
    if not result:
        print('[Not normal][yijiefeng] %s' % contents)
    return result


def jiefengExtract(contents, time_str, resource):
    '''

    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    jiefengPattern = re.compile('(?P<serial_number>解封-\d+-\d+.*?)】.*?(?P<ip_list>.{7,}?)请解封', re.I)
    items = re.finditer(jiefengPattern, contents)

    for it in items:
        item_dict = it.groupdict()
        ips = ipExtract(item_dict['ip_list'])
        if not ips:
            print('[Not normal][jiefeng][IP error] %s' % item_dict)
            continue
        item_dict['ip_list'] = ips
        item_dict['income_time'] = time_str
        item_dict['resource'] = resource
        result.append(item_dict)
    if not result and len(contents) > 13:
        print('[Not normal][jiefeng] %s' % contents)
        result.append(
            {'serial_number': contents, 'income_time': time_str, 'resource': resource, 'ip_list': ' '})
    return result


def yifengduExtract(contents, time_str, resource):
    '''
    从字符串中提取已封堵信息
    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,resource,time},{...},...]
    '''
    result = []
    serial_list = []
    yifengduPattern = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)已封堵', re.I)
    yifengduPattern1 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)ipv6', re.I)
    yifengduPattern2 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)封堵过', re.I)
    yifengduPattern3 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)已经封堵', re.I)
    yifengduPattern4 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)没有封堵', re.I)
    yifengduPattern5 = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)封堵成功', re.I)

    wc_index = contents.find('已封堵')
    v6_index = contents.find('ipv6')
    fdg_index = contents.find('封堵过')
    yjfd_index = contents.find('已经封堵')
    myfd_index = contents.find('没有封堵')
    fdcg_index = contents.find('封堵成功')
    index_dict = {
        'wancheng': [wc_index, wc_index + 3, '已封堵', yifengduPattern],
        'ipv6': [v6_index, v6_index + 4, '不支持ipv6', yifengduPattern1],
        'fdg': [fdg_index, fdg_index + 3, '封堵过', yifengduPattern2],
        'yjfd': [yjfd_index, yjfd_index + 4, '已经封堵', yifengduPattern3],
        'myfd': [myfd_index, myfd_index + 4, '没有封堵', yifengduPattern4],
        'fdcg': [fdcg_index, fdcg_index + 4, '封堵成功', yifengduPattern5],
    }
    index_dict = sorted(index_dict.items(), key=lambda x: x[1][0])
    content_index = 0  # 切分content为不同的字符串
    for k, v in index_dict:
        if v[0] == -1:
            continue
        content = contents[content_index:v[1]]
        content_index = v[1]
        extract_list = yifengduSubExtract(content, v[-1])
        if not extract_list:
            print('[Not normal][yifengdu][sub extract] %s' % content)
            continue
        for el in extract_list:
            item_dict = {'serial_number': el, 'outcome_time': time_str, 'excutor': resource, 'outcome': v[2]}
            if item_dict not in result:
                result.append(item_dict)
    if not result:
        print('[Not normal][yifengdu] %s' % contents)
    return result


def yifengduSubExtract(contents, yifengduPattern):
    sub_pattern = re.compile('.*?(?P<serial_number>FD-\d+-\d+)', re.I)
    serialnumber_str = yifengduPattern.match(contents)
    if not serialnumber_str:
        print('[Not normal][yifengdu] %s' % contents)
        return False
    serialnumbers = re.finditer(sub_pattern, serialnumber_str.groupdict()['serial_number'])
    items = []
    for it in serialnumbers:  # 这里可以确定匹配成功
        item = it.groupdict()['serial_number']
        items.append(item)
    return compeleteContinueNumber(contents, items)


def fengduExtract(contents, time_str, resource):
    '''
    从字符串中提取封堵信息
    :param contents:
    :param time_str:
    :param resource:
    :return: [{serial_number,incoming_time,...},{...},...]
    '''
    result = []
    fengduPattern = re.compile(
        '(?P<serial_number>FD-\d+-\d+).*?\d+日.*?(?P<hour>\d+).*?(?P<min>\d+).*?IP[:：].*?(?P<ip_list>.*?)[因|尝试](?P<reason>.*?)请相关部门',
        re.I)
    items = re.finditer(fengduPattern, contents)

    for it in items:
        item_dict = it.groupdict()
        item_dict['income_time'] = time_str
        item_dict['resource'] = resource
        item_dict['number_time'] = item_dict['hour'] + ':' + item_dict['min']
        item_dict.pop('hour')
        item_dict.pop('min')

        ips = ipExtract(item_dict['ip_list'])
        if not ips:
            print('[Not normal][fengdu][IP error] %s' % item_dict)
            continue
        item_dict['ip_list'] = ips
        result.append(item_dict)
    if not result and len(contents) > 20:
        number_time = ':'.join(time_str.split(' ')[-1].split(':')[:2])
        extract_list = fengduExtract2(contents)
        if not extract_list:
            print('[Not normal][fengdu] %s' % contents)
            result.append(
                {'serial_number': ' ', 'number_time': ' ', 'resource': resource, 'ip_list': ' ', 'reason': contents,
                 'income_time': time_str})
        else:
            for el in extract_list:
                if '附件' in contents:
                    ip_list = '详见附件'
                else:
                    ip_list = '详见处置原因'
                item_dict = {'serial_number': el, 'number_time': 'number_time', 'resource': resource,
                             'ip_list': ip_list, 'reason': contents, 'income_time': time_str}
                if item_dict not in result:
                    result.append(item_dict)
    return result


def fengduExtract2(contents):
    '''
    补充提取封堵信息
    :param contents:
    :return:
    '''
    fengduPattern = re.compile('.*?(?P<serial_number>FD-\d+-\d+.*?)', re.I)
    return yifengduSubExtract(contents, fengduPattern)


def compeleteContinueNumber(contents, items):
    '''
    补充完整序号，如1-3，1到3
    :param contents:
    :param items:
    :return: []
    '''
    result = []
    if len(items) == 1:
        return items
    step_indexs = [i.start() for i in re.finditer(r'[-—~到至]', contents)]
    item_indexs = []
    for it in items:
        item_indexs.extend([contents.index(it), contents.index(it) + len(it)])
    # 排除在item中的字符串
    e_indexs = []
    for i in step_indexs:  # 找到特殊字符串的位置
        for j in items:
            if i in range(contents.index(j), contents.index(j) + len(j)):
                e_indexs.append(i)
    for i in e_indexs:
        if i in step_indexs:
            step_indexs.remove(i)
    # 没有连续编号，直接返回
    if not step_indexs:
        return items
    # 需要拆分的数据
    split_tuple = []
    j_index = 0
    for i in range(len(item_indexs)):
        i_num = item_indexs[i]
        j_num = step_indexs[j_index]
        if j_num > item_indexs[-1]:
            print('[WARNING] something should be pay attention. %s' % contents)
            break
        if j_num > i_num and j_num < item_indexs[i + 1]:
            t = (items[int((i + 1) / 2) - 1], items[int((i + 1) / 2)])
            if not t in split_tuple:
                split_tuple.append(t)
            t_index = j_index
            for k in range(t_index, len(step_indexs)):
                if step_indexs[k] < item_indexs[i + 1] and j_index + 1 < len(step_indexs):
                    j_index += 1

    for (start, end) in split_tuple:
        label, date, s = start.split('-')
        label, date, e = end.split('-')
        items.remove(start)
        items.remove(end)
        for i in range(int(s), int(e) + 1):
            if label == 'FD':
                item = '%s-%s-%03d' % (label, date, i)
            else:
                item = '%s-%s-%02d' % (label, date, i)
            if item not in result:
                result.append(item)
    if items:
        result.extend(items)
    return result


def ipExtract(ip_str):
    '''
    从字符串中提取IP地址
    :param ip_str:
    :return: 纯ip自字符串
    '''
    ip_list = []
    # 默认给出的IP地址都是正确的
    ip_regex = re.compile('([0-9a-f/.:]{7,})', re.I)
    ipv4_regex = re.compile('((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)[/\d]{0,3]')
    ip6_regex = re.compile('(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,6}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,5}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4}){1,4}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]{1,4}){1,3}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,5}(:[0-9a-f]{1,4}){1,2}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,6}(:[0-9a-f]{1,4}){1,1}\Z)|'
                           '(\A(([0-9a-f]{1,4}:){1,7}|:):\Z)|(\A:(:[0-9a-f]{1,4})'
                           '{1,7}\Z)|(\A((([0-9a-f]{1,4}:){6})(25[0-5]|2[0-4]\d|[0-1]'
                           '?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|'
                           '(\A(([0-9a-f]{1,4}:){5}[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|'
                           '[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3})\Z)|'
                           '(\A([0-9a-f]{1,4}:){5}:[0-9a-f]{1,4}:(25[0-5]|2[0-4]\d|'
                           '[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)|'
                           '(\A([0-9a-f]{1,4}:){1,1}(:[0-9a-f]{1,4}){1,4}:(25[0-5]|'
                           '2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d))'
                           '{3}\Z)|(\A([0-9a-f]{1,4}:){1,2}(:[0-9a-f]{1,4}){1,3}:'
                           '(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?'
                           '\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,3}(:[0-9a-f]{1,4})'
                           '{1,2}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|'
                           '[0-1]?\d?\d)){3}\Z)|(\A([0-9a-f]{1,4}:){1,4}(:[0-9a-f]'
                           '{1,4}){1,1}:(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|'
                           '2[0-4]\d|[0-1]?\d?\d)){3}\Z)|(\A(([0-9a-f]{1,4}:){1,5}|:):'
                           '(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?'
                           '\d?\d)){3}\Z)|(\A:(:[0-9a-f]{1,4}){1,5}:(25[0-5]|2[0-4]\d|'
                           '[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\Z)')
    if not ip_str.strip():
        return 'IP empty'
    ips = re.finditer(ip_regex, ip_str)
    if not ips:
        print('[Not normal][IP error]%s' % ip_str)
        return False
    for ip in ips:
        ip_list.append(ip.group())
    return '\n'.join(ip_list)


def playMusic(items):
    '''
    判断是否播放音乐
    :param item:
    '''
    flag = False
    for item in items:
        if 'location' in item:
            if '深圳' in item['location']:
                print('[INFO] find [深圳] Need check! ', item)
                flag = True
            else:
                flag = False
        else:
            print('[INFO] Need check! ', item)
            flag = True
    if flag:
        play()


def play():
    '''
    播放音乐
    '''
    print('{:*^80}'.format('Play music'))
    os.system('D:\\PycharmProjects\\sharezone\\doc\\clock.mp3')


def updateDatabase():
    data_dict = feixinInfo2DB()
    for k, v in data_dict.items():
        if k in tableClass:
            print('[INFO] Insert %s into %s' % (len(v),k))
            insertBulk(k, v)
        elif k == 'yifengdu':
            print('[INFO] Update %s into %s' % (len(v),k))
            updateBulk('fengdu', v, 'serial_number')
        elif k == 'yijiefeng':
            print('[INFO] Update %s into %s' % (len(v),k))
            updateBulk('jiefeng', v, 'serial_number')

# content = '【FD-0619-445】深基封堵完成'
# jichufdExtract(content,'test','test')
# content2 = 'PC-0608-028【内网网络事件】请相关部门排查：被攻击ip:192.168.31.240 物理位置:三期南北 攻击手段:怀疑被植入挖矿后门 防护措施:建议排查主机'
# paichaExtract2(content2, 'test', 'test')
# updateDatabase()
# play()
