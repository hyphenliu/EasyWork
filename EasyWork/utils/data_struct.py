#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : edata_struct.py
@Author: HP.Liew
@Date  : 2019/11/14 16:38
@Desc  : 整合历史代码
'''
from inventory.models import *
from networkops.models import *
from dailywork.models import *

# 数据库表
tableClass = {
    'contact': Contact, 'sox': SOX,
    ############################################################################
    'fengdu': Fengdu, 'jiefeng': Jiefeng, 'paicha': PaiCha, 'jichufd': Jichufd, 'jichujf': Jichujf,
    'iplist': IPList, 'baozhang': Baozhang, 'accesslist': AccessList, 'ippatmapping': IPPATMapping,
    'ipmapping': IPMapping,
    ###########################################################################
    'erp': AssetsERP, 'schedual': AssetsSchedual, 'inventoried': AssetsInventoried,
    'inventory': AssetsInventory, 'prescrap': AssetsPrescrap, 'scraped': AssetsScraped,
    ###########################################################################
}
# # 数据库表结构，自动获取
# table_colums = {}
# with open('original.py','r',encoding='utf-8') as f:
#     flag = False
#     file_content = f.readlines()
#     for line in file_content:
#         line = line.strip()
#         if line.startswith('class') and line.endswith('(models.Model):'):
#             flag = True
#             key = line.split()[1].split('(')[0].lower()[6:]
#             table_colums[key] = []
#         elif line.startswith('class'):
#             flag = False
#         if '=' in line and key:
#             table_colums[key].append(line.split('=')[0].strip())
tableColums = {
    'iplist': ['ip', 'location', 'belong', 'type', 'note'],
    'accesslist': ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
                   'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain'],
    'ippatmapping': ['province', 'source_ip', 'source_port', 'dest_ip', 'dest_port', 'ip_type', 'net_work', 'system'],
    'ipmapping': ['province', 'source_ip', 'dest_ip', 'system'],
    ########################################
    'fengdu': ['serial_number', 'income_time', 'number_time', 'resource', 'ip_list', 'reason', 'excutor', 'outcome',
               'outcome_time', 'note'],
    'jiefeng': ['serial_number', 'income_time', 'resource', 'ip_list', 'excutor', 'outcome', 'outcome_time', 'note'],
    'paicha': ['serial_number', 'reason', 'ip_attack', 'ip_attacked', 'location', 'means', 'guard', 'result',
               'income_time', 'resource'],
    'jichufd': ['serial_number', 'income_time', 'resource', 'outcome'],
    'jichujf': ['serial_number', 'income_time', 'resource', 'outcome'],
    'baozhang': ['reason', 'ip_source', 'ip_dest', 'income_time', 'resource', 'level'],
    ###########################################################################
    'contact': ['organization', 'department', 'name', 'address', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
    'sox': ['staff', 'stand_point', 'province_point', 'area', 'procedure', 'sub_procedure', 'control_goal',
            'company_describe', 'standard_describe', 'frequency', 'control_type', 'control_method', 'department_list',
            'duty', 'classification', 'reference_file', 'focus_point', 'test_file', 'update'],
    ###########################################################################
    'erp': ['asset_code', 'asset_label', 'asset_name', 'asset_type', 'type_describe', 'serial_number', 'keyword',
            'manufactor', 'model', 'number', 'unit_type', 'import_date', 'use_date', 'depreciate_date',
            'depreciate_method', 'limit_year', 'remainder_month', 'cost', 'remainder_value', 'remainder_count',
            'residual_value', 'month_depreciate', 'year_depreciate', 'accumulate_depreciate', 'month_diminution',
            'year_diminution', 'accumulate_diminution', 'staff_code', 'staff_name', 'address', 'address_describe',
            'early_code', 'early_label', 'early_project_id', 'project_status', 'project_source', 'project_id',
            'project_name', 'other_attachment', 'bounch7', 'bounch8', 'bounch9', 'bounch10', 'cost_account',
            'cost_account_describe', 'depreciate_account', 'depreciate_account_describe', 'accumulate_account',
            'accumulate_account_describe', 'budgets_company', 'budgets_department', 'budgets_project',
            'budgets_service', 'budgets_subject', 'service_platform', 'network_level', 'coconstruct',
            'budgets_contract', 'actual_number', 'deduction_label', 'finacial_type', 'scrap_date'],
    'schedual': ['asset_label', 'asset_name', 'model', 'manufactor', 'address', 'staff_department', 'staff_name',
                 'note', 'schedual_date'],
    'inventoried': ['asset_label', 'asset_name', 'model', 'manufactor', 'address', 'staff_department', 'staff_name',
                    'note', 'schedual_date'],
    'inventory': ['machine_address', 'machine_room', 'machine_column', 'machine_racket', 'asset_label', 'asset_name',
                  'model', 'manufactor', 'staff_name', 'note', 'inventory_date'],
    'prescrap': ['asset_label', 'asset_name', 'model', 'staff_name', 'address', 'noservice', 'nopower', 'need_erase',
                 'cable_extract', 'can_move', 'prescraped_label', 'cost', 'use_date', 'remainder_month',
                 'remainder_value', 'note', 'prescraped_date'],
    'scraped': ['asset_label', 'asset_name', 'model', 'manufactor', 'staff_department', 'staff_name'],
    ###########################################################################
}

tableTitles = {
    'iplist': ['IP地址', '位置', '归属', '黑白名单', '备注'],
    'accesslist': ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                   '接入IP承载网所属VPN域'],
    'ippatmapping': ['省份', '源地址', '源端口', '映射地址', '映射端口', '类型', '网络号', '系统'],
    'ipmapping': ['省份', '源地址', '映射地址', '系统'],
    ########################################
    'fengdu': ['编号', '需求时间', '编号时间', '需求来源', '处置IP地址', '处置原因', '处置者', '处置结果', '处理时间', '备注'],
    'jiefeng': ['编号', '需求时间', '需求来源', '解封IP地址', '解封者', '解封结果', '解封时间', '备注'],
    'paicha': ['编号', '原因', '攻击IP', '被攻击IP', '物理位置', '攻击手段', '防护措施', '排查结果', '需求时间', '需求来源'],
    'jichufd': ['编号', '封堵时间', '封堵者', '封堵结果'],
    'jichujf': ['编号', '解封时间', '解封者', '解封结果'],
    'baozhang': ['告警内容', '源IP', '目的IP', '告警时间', '告警来源', '告警级别'],
    ###########################################################################
    'contact': ['公司', '部门', '姓名', '办公地点', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
    'sox': ['部门责任人', '标准控制点编号', '公司控制点编号', '适用范围', '业务流程', '子流程', '控制目标', '公司控制点描述', '标准控制点描述', '发生频率', '控制类型', '控制方式',
            '具体部门', '控制点负责人', '控制点分类', '参考文件', '建议关注点', '参考的穿行测试资料', '添加时间'],
    ###########################################################################
    'erp': ['资产编号', '资产标签号', '资产名称', '资产类别', '资产类别描述', '序列号', '资产关键字', '厂商', '规格型号', '数量', '单位', '创建日期', '启用日期',
            '按比例分摊日期', '折旧方法', '使用年限', '剩余月数', '成本', '资产净值', '资产净额', '残值', '本期折旧额', '本年折旧额', '累计折旧额', '本期减值准备',
            '本年减值准备', '累计减值准备', '员工编号', '员工姓名', '地点', '地点说明', '期初资产卡片编号', '期初资产标签编号', '期初估列项目编号', '建设状态', '资产来源',
            '项目编号', '项目名称', '其他附加信息', '弹性域信息7', '弹性域信息8', '弹性域信息9', '弹性域信息10', '成本帐户', '成本帐户描述', '折旧帐户', '折旧帐户描述',
            '累计折旧帐户', '累计折旧帐户描述', '预算公司段', '预算责任部门', '预算项目', '预算业务活动', '预算科目', '业务平台', '网络层次', '是否共建', '预算合同信息', '实际数量',
            '资产抵扣标识', '财产类型'],
    'schedual': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventoried': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventory': ['机房地点', '机房位置', '机架列', '机架号', '资产编码', '设备名称', '规格', '制造商', '责任人', '备注'],
    'prescrap': ['资产标签号', '资产名称', '规格型号', '责任人', '位置', '业务上不能再使用', '下电', '设备消磁', '连接线拆除', '达到可以搬离状态', '已进行拟报废标示', '原值',
                 '启用日期', '折旧剩余月数', '资产净额', '备注'],
    'scraped': ['资产标签号', '设备名称', '规格', '制造商', '管理部门', '责任人'],
    ###########################################################################
}

htmlTitles = {
    'iplist': ['IP地址', '位置', '归属', '黑白名单', '备注'],
    'accesslist': ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                   '接入IP承载网所属VPN域'],
    'ippatmapping': ['省份', '源地址', '源端口', '映射地址', '映射端口', '类型', '网络号', '系统'],
    'ipmapping': ['省份', '源地址', '映射地址', '系统'],
    ########################################
    'fengdu': ['编号', '编号时间', '需求来源', '处置IP地址', '处置原因', '处置者', '处置结果', '处理时间', '备注', '添加时间'],
    'jiefeng': ['编号', '需求时间', '需求来源', '解封IP地址', '解封者', '解封结果', '解封时间', '备注'],
    'paicha': ['编号', '原因', '攻击IP', '被攻击IP', '物理位置', '攻击手段', '防护措施', '排查结果', '需求时间', '需求来源', '添加时间'],
    'jichufd': ['编号', '封堵时间', '封堵者', '封堵结果'],
    'jichujf': ['编号', '解封时间', '解封者', '解封结果'],
    'baozhang': ['告警内容', '源IP', '目的IP', '告警时间', '告警来源', '告警级别'],
    ###########################################################################
    'contact': ['部门', '姓名', '办公地点', '邮箱', '电话', '职务', '更新日期'],
    'taxi': ['日期', '时间', '单价'],
    'sox': ['部门责任人', '标准编号', '公司编号', '控制目标', '公司控制点描述', '频率', '类型', '具体部门', '负责人', '参考文件',
            '参考穿测资料', '添加时间'],
    ###########################################################################
    'erp': ['资产标签号', '资产名称', '厂商', '规格型号', '创建日期', '启用日期', '使用年限', '剩余月数', '成本', '资产净额', '员工编号', '员工姓名', '地点',
            '期初资产标签编号',
            '项目编号', '项目名称', '其他附加信息'],
    'schedual': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventoried': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventory': ['机房地点', '机房位置', '机架列', '机架号', '资产编码', '设备名称', '规格', '制造商', '责任人', '备注'],
    'prescrap': ['资产标签号', '资产名称', '规格型号', '责任人', '位置', '业务上不能再使用', '下电', '设备消磁', '连接线拆除', '达到可以搬离状态', '已进行拟报废标示', '原值',
                 '启用日期', '折旧剩余月数', '资产净额', '备注'],
    'scraped': ['资产标签号', '设备名称', '规格', '制造商', '管理部门', '责任人'],
    ###########################################################################
}

htmlColums = {
    'iplist': ['ip', 'location', 'belong', 'type', 'note'],
    'accesslist': ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
                   'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain'],
    'ippatmapping': ['province', 'source_ip', 'source_port', 'dest_ip', 'dest_port', 'ip_type', 'net_work', 'system'],
    'ipmapping': ['province', 'source_ip', 'dest_ip', 'system'],
    ########################################
    'fengdu': ['serial_number', 'number_time', 'resource', 'ip_list', 'reason', 'excutor', 'outcome',
               'outcome_time', 'note'],
    'jiefeng': ['serial_number', 'income_time', 'resource', 'ip_list', 'excutor', 'outcome', 'outcome_time', 'note',
                'time'],
    'paicha': ['serial_number', 'reason', 'ip_attack', 'ip_attacked', 'location', 'means', 'guard', 'result',
               'income_time', 'resource', 'time'],
    'jichufd': ['serial_number', 'income_time', 'resource', 'outcome'],
    'jichujf': ['serial_number', 'income_time', 'resource', 'outcome'],
    'baozhang': ['reason', 'ip_source', 'ip_dest', 'income_time', 'resource', 'level'],
    ###########################################################################
    'contact': ['department', 'name', 'address', 'email', 'phone', 'duty', 'update'],
    'taxi': ['date', 'time', 'price'],
    'sox': ['staff', 'stand_point', 'province_point', 'control_goal', 'company_describe', 'frequency', 'control_type',
            'department_list', 'duty', 'reference_file', 'test_file', 'update'],
    ###########################################################################
    'erp': ['asset_label', 'asset_name', 'manufactor', 'model', 'import_date', 'use_date', 'limit_year',
            'remainder_month', 'cost', 'remainder_count', 'staff_code', 'staff_name', 'address', 'early_label',
            'project_id',
            'project_name', 'other_attachment'],
    'schedual': ['asset_label', 'asset_name', 'model', 'manufactor', 'address', 'staff_department', 'staff_name',
                 'note'],
    'inventoried': ['asset_label', 'asset_name', 'model', 'manufactor', 'address', 'staff_department', 'staff_name',
                    'note'],
    'inventory': ['machine_address', 'machine_room', 'machine_column', 'machine_racket', 'asset_label', 'asset_name',
                  'model', 'manufactor', 'staff_name', 'note', 'inventory_date'],
    'prescrap': ['asset_label', 'asset_name', 'model', 'staff_name', 'address', 'noservice', 'nopower', 'need_erase',
                 'cable_extract', 'can_move', 'prescraped_label', 'cost', 'use_date', 'remainder_month',
                 'remainder_value', 'note'],
    'scraped': ['asset_label', 'asset_name', 'model', 'manufactor', 'staff_department', 'staff_name'],
    ###########################################################################
}

fileNames = {
    'iplist': 'IP名单',
    'accesslist': '网络策略开通',
    'ippatmapping': 'PAT映射表',
    'ipmapping': 'CZW映射表',
    ########################################
    'fengdu': 'HW封堵',
    'jiefeng': 'HW解封',
    'paicha': 'HW排查',
    'jichufd': '深圳封堵',
    'jichujf': '深圳解封',
    ###########################################################################
    'contact': '联系人列表',
    'taxi': '交通票据',
    'sox': 'SOX内控矩阵',
    ###########################################################################
    'erp': '资产明细',
    'schedual': '盘点清册',
    'inventory': '盘点结果',
    'prescrap': '拟报废清单',
    'scraped': '已报废清单',
    ###########################################################################
}
