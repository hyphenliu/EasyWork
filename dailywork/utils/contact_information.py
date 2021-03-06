# -*- coding:utf-8 -*-
import urllib, re, json, time, random, datetime
from http import cookiejar
from urllib import request, parse
from collections import defaultdict
from django.core.cache import cache
from dailywork.utils.phone import Phone
from EasyWork.utils.database_ops import *


class OA:
    def __init__(self, domain, user, password):
        '''
        初始化一些变量
        :param domain:域名 
        :param user: 用户
        :param password:用户登录密码 
        '''
        # 第一步请求
        self.domain = domain
        self.loginUrl = "http://eip.{}".format(self.domain)
        self.loginHeaders = {
            'Host': 'eip.{}'.format(domain),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Connection': 'keep-alive'
        }
        self.paramsDict = self._getFirstLoginInfo()
        if not self.paramsDict:
            return
        self.loginHeaders['Referer'] = self.loginUrl
        self.loginHeaders['Host'] = 'sso.{}'.format(self.domain)
        self.loginHeaders['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.post = post = {
            'userid': user,
            'password': password,
            'apptempid': self.paramsDict['apptempid'],
            'success': self.paramsDict['success'],
            'token': self.paramsDict['token']
        }
        self.loginUrl = 'http://sso.{}/sso/login'.format(self.domain)
        self.postData = parse.urlencode(self.post).encode('utf-8')
        self.cookie = cookiejar.LWPCookieJar()
        self.cookieHandler = request.HTTPCookieProcessor(self.cookie)
        self.opener = request.build_opener(self.cookieHandler, request.HTTPHandler)

    def _getFirstLoginInfo(self):
        '''
        获取登录的cookies信息：token， success， apptempid
        :return:
        '''
        extractPattern = re.compile(
            '.+?token=(?P<token>.+?)&success=(?P<success>.+?)&apptempid=(?P<apptempid>.+?)$')
        req = request.Request(self.loginUrl)
        httpHandler = request.HTTPHandler()
        opener = request.build_opener(httpHandler)
        try:
            response = opener.open(req)
        except Exception as e:
            print(e)
            return
        status = response.getcode()
        if status == 200:
            self.loginUrl = response.url
            items = extractPattern.match(self.loginUrl.strip())
            if items:
                return items.groupdict()
            else:
                print('[ERROR] 解析url失败： {}'.format(self.loginUrl))
                return
        else:
            print('[ERROR] 请求失败: {}'.format(self.loginUrl))
            return

    def login(self):
        '''
        登录到首页
        :return:
        '''
        result = {'error': '', 'success': ''}
        req = request.Request(self.loginUrl, self.postData, headers=self.loginHeaders)
        response = self.opener.open(req)
        status = response.getcode()
        if status == 200:
            response = self.opener.open(request.Request('http://eip.%s/' % self.domain))  # 登录首页
            content = response.read().decode('utf-8')
            if not '统一信息平台' in content:
                result['error'] = '登录用户名或密码错误'
            else:
                result['success'] = 'success'
        else:
            result['error'] = '请求登录页面失败'
        return result

    def _logout(self):
        '''
        退出登录
        :return:
        '''
        self.opener.open(request.Request('http://eip.%s/index.php/Home/User/logout.html' % self.domain))

    def _extractContact(self, content, org, dep):
        '''
        提取联系人信息
        :param content:
        :param org:
        :param dep:
        :return:
        '''
        p = Phone()
        datas = content['data']
        result = []
        for data in datas:
            name = data.get('cn', 'name not find').strip()
            email = data.get('email', 'email not find').strip()
            phone = data.get('preferredMobile', '').strip()
            if not phone:
                phone = '字段为空'
                address = '电话号码为空，无法取得地址信息'
                print(f'{name}的手机字段不存在')
            else:
                address = p.main(phone)
                if not address:
                    address = ' '
                    print(f'{name}的手机{phone}没有找到归属地')
                else:
                    address = address.split('|')[1]
            level = data.get('level', '新员工').strip()
            result.append([org, dep, name, address, email, phone, level, '在职'])  # 按照data_struct.py中设定的顺序排列
        return result

    def _extractOID(self, datas, level=1, parent_o='', parent_name=''):
        '''
        获取组织树状图信息
        :param level:层级
        :param parent_o:完整路径
        :param parent_name:完整路径名
        :return:
        '''
        result = {}
        for data in datas:
            display_name = data.get('displayName', 'displayName not exist').strip()
            org = data.get('o', 'o not exist').strip()
            parent_org = data.get('parentOrgId', 'parentOrgId not exist').strip()
            o_path = '|'.join([parent_o, org])
            o_name_path = '|'.join([parent_name, display_name])
            result[display_name] = {'o': org, 'parent_org': parent_org, 'level': level}
            if 'children' in data:
                level += 1
                result[display_name]['children'] = self._extractOID(data['children'], level, o_path, o_name_path)
                level -= 1
        return result

    def _readResJSON(self, response):
        '''
        读取api返回的json数据
        :param response:
        :return:
        '''
        return json.loads(response.read().decode('utf-8'), encoding='utf-8')

    def _timeStamp(self):
        return int(round(time.time() * 1000))

    def _getContact_(self, org_type='直属单位', org='信息技术中心（公司）'):
        '''
         获取用户通讯录，返回列表【公司，部门，姓名，邮箱，电话，职务】
        :return:[[org, dep, name, email, phone, level],...]
        '''
        login_result = self.login()
        # 登录失败直接返回
        if not login_result['success']:
            return login_result
        result = []
        self.org_tree = defaultdict(list)
        url_prefix = 'http://cloudapps.{}/ua/'.format(self.domain)
        contact_index_url_prefix = url_prefix + 'index{}.do{}'
        contact_tree_api_prefix = url_prefix + 'api/{}?biz_type={}&o={}&_t={}'
        contact_info_api_prefix = url_prefix + 'api/userbyorg?biz_type={}&o={}&_t={}'

        org_tree = 'orgtree'
        if org_type in ['直属单位', '专业公司', '集团总部']:
            biz_type = '1'
            index_type = '0'
            if org_type == '集团总部':
                oid = '1'
                gid = 'hq'
            elif org_type == '专业公司':
                oid = '2691'
                gid = 'zygs'
            else:
                oid = '2641'
                gid = 'zsdw'
            penix = '?o=' + oid + '&grouptenentid=t.ua.' + gid
        elif org_type in ['省公司', '有限公司']:
            if org_type == '省公司':
                index_type = biz_type = '3'
                oid = ''
                org_tree = 'orgs'
            else:
                index_type = biz_type = '2'
                oid = 'C00020000000000000000'
            penix = '00000000000000000000'
        else:
            return
        contact_index_url = contact_index_url_prefix.format(index_type, penix)
        contact_tree_api = contact_tree_api_prefix.format(org_tree, biz_type, oid, self._timeStamp())
        print(contact_index_url)
        self.opener.open(request.Request(contact_index_url))  # 访问通讯录页面，不能跳过
        time.sleep(random.randint(1, 3))  # 随机休眠1-3秒
        print(contact_tree_api)
        response = self.opener.open(request.Request(contact_tree_api))  # 获取通讯录的公司组织结构树状图json信息
        json_content = self._readResJSON(response)  # 读取json信息
        org_rst = self._extractOID(json_content['data']['children'])  # 获取类型下所有机构的树状json信息
        org_dep = org_rst[org_type]['children'][org]['children']  # 获取指定公司的树状json信息，这里指定信息技术中心部门
        dep_list = self._getDepChildrenOid(org_dep)
        for idx, oname in enumerate(dep_list):
            contact_info_api = contact_info_api_prefix.format(biz_type, dep_list[oname], self._timeStamp())
            print(contact_info_api)
            # time.sleep(random.randint(3, 5))  # 随机休眠1-3秒
            response = self.opener.open(request.Request(contact_info_api))  # 获取部门联系人json信息
            json_content = self._readResJSON(response)  # 读取json信息
            result.extend(self._extractContact(json_content, org, oname.strip()))
            # 更新进度条
            cache.set('{}ProgressNum'.format('contact'), '{:.1f}'.format(1.0 * 100 * (idx + 1) / len(dep_list)), 5)
        self._logout()

        return {'success': result, 'error': ''}

    def _getDepChildrenOid(self, dep_dict, depname=''):
        '''
        获取部门下设的二级部门
        :param dep_dict:
        :param depname:上级部门名称
        :return:
        '''
        dep_name = {}
        for k, v in dep_dict.items():
            if depname:
                k = '{}|{}'.format(depname, k)
            dep_name[k] = v['o']
            if 'children' in v:
                dep_name.update(self._getDepChildrenOid(v['children'], k))
        return dep_name

    def getContactInfo(self, org_type='直属单位', org='信息技术中心（公司）'):
        result = self._getContact_(org_type, org)
        if not result['success']: return result
        db_dict = {}
        db_list = defaultdict(int)
        updata_item = []
        insert_item = []
        item_type = ['organization', 'department', 'name', 'address', 'email', 'phone', 'duty', 'status']
        # ['organization', 'department', 'name', 'address', 'email', 'phone', 'duty', 'status']
        datas = result['success']
        db_data = getAll('contact').values()

        for dd in db_data:  # 以邮箱和部门为唯一值
            db_list[dd['email']] += 1
        for dd in db_data:
            if db_list[dd['email']] > 1 and dd['status'] == '离职':  # 删除无效数据
                removeData('contact', {'email': dd['email'], 'status': '离职'})
            else:
                db_dict['{}{}'.format(dd['department'].strip(), dd['email']).strip()] = dd
        for data in datas:
            print(data)
            k = f'{data[1]}{data[4]}'
            if k in db_dict:
                db_dict.pop(k)  # 删除已经存在的数据
            elif data[4] in db_list and not '处长' in data[-2]:  # 更新跨部门调动的员工
                item = getFilterColumns('contact', {'email': data[4]}, filter='iexact').values()[0]
                db_dict.pop('{}{}'.format(item['department'], item['email']))
                updateSingle('contact', dict(zip(item_type, data)), 'email')
            else:
                insert_item.append(data)  # 新入职员工
        # 已离职人员，只取值value，不取键key
        for _, v in db_dict.items():
            v['update'] = datetime.datetime.now()
            v['status'] = '离职'
            updata_item.append(v)
        error = result['error']
        print(insert_item, updata_item)
        return {'insert': insert_item, 'update': updata_item, 'error': error}
# oa = OA()
# oa.main()
