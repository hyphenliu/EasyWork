from networkops.models import *

# 数据库表
tableClass = {'fengdu': Fengdu, 'jiefeng': Jiefeng, 'paicha': PaiCha, 'jichufd': Jichufd, 'jichujf': Jichujf,
              'iplist': IPList, 'baozhang': Baozhang, 'accesslist': AccessList}
tableColums = {
    'fengdu': ['serial_number', 'income_time', 'number_time', 'resource', 'ip_list', 'reason', 'excutor', 'outcome',
               'outcome_time', 'note'],
    'jiefeng': ['serial_number', 'income_time', 'resource', 'ip_list', 'excutor', 'outcome', 'outcome_time', 'note'],
    'paicha': ['serial_number', 'reason', 'ip_attack', 'ip_attacked', 'location', 'means', 'guard', 'result',
               'income_time', 'resource'],
    'jichufd': ['serial_number', 'income_time', 'resource', 'outcome'],
    'jichujf': ['serial_number', 'income_time', 'resource', 'outcome'],
    'baozhang': ['reason', 'ip_source', 'ip_dest', 'income_time', 'resource', 'level'],
    'iplist': ['ip', 'location', 'belong', 'type', 'note'],
    'accesslist': ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
                   'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']
}

tableTitles = {
    'fengdu': ['编号', '需求时间', '编号时间', '需求来源', '处置IP地址', '处置原因', '处置者', '处置结果', '处理时间', '备注'],
    'jiefeng': ['编号', '需求时间', '需求来源', '解封IP地址', '解封者', '解封结果', '解封时间', '备注'],
    'paicha': ['编号', '原因', '攻击IP', '被攻击IP', '物理位置', '攻击手段', '防护措施', '排查结果', '需求时间', '需求来源'],
    'jichufd': ['编号', '封堵时间', '封堵者', '封堵结果'],
    'jichujf': ['编号', '解封时间', '解封者', '解封结果'],
    'baozhang': ['告警内容', '源IP', '目的IP', '告警时间', '告警来源', '告警级别'],
    'iplist': ['IP地址', '位置', '归属', '黑白名单', '备注'],
    'accesslist': ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                   '接入IP承载网所属VPN域']
}

htmlTitles = {
    'fengdu': ['编号', '编号时间', '需求来源', '处置IP地址', '处置原因', '处置者', '处置结果', '处理时间', '备注', '添加时间'],
    'jiefeng': ['编号', '需求时间', '需求来源', '解封IP地址', '解封者', '解封结果', '解封时间', '备注'],
    'paicha': ['编号', '原因', '攻击IP', '被攻击IP', '物理位置', '攻击手段', '防护措施', '排查结果', '需求时间', '需求来源', '添加时间'],
    'jichufd': ['编号', '封堵时间', '封堵者', '封堵结果'],
    'jichujf': ['编号', '解封时间', '解封者', '解封结果'],
    'baozhang': ['告警内容', '源IP', '目的IP', '告警时间', '告警来源', '告警级别'],
    'iplist': ['IP地址', '位置', '归属', '黑白名单', '备注'],
    'accesslist': ['访问方向', '源地址', '源地址对应的映射IP', '源端口', '目的地址', '目的地址对应的映射IP', '目的端口', '传输层协议', '应用层协议', '策略用途',
                   '接入IP承载网所属VPN域']
}

htmlColums = {
    'fengdu': ['serial_number', 'number_time', 'resource', 'ip_list', 'reason', 'excutor', 'outcome',
               'outcome_time', 'note'],
    'jiefeng': ['serial_number', 'income_time', 'resource', 'ip_list', 'excutor', 'outcome', 'outcome_time', 'note',
                'time'],
    'paicha': ['serial_number', 'reason', 'ip_attack', 'ip_attacked', 'location', 'means', 'guard', 'result',
               'income_time', 'resource', 'time'],
    'jichufd': ['serial_number', 'income_time', 'resource', 'outcome'],
    'jichujf': ['serial_number', 'income_time', 'resource', 'outcome'],
    'baozhang': ['reason', 'ip_source', 'ip_dest', 'income_time', 'resource', 'level'],
    'iplist': ['ip', 'location', 'belong', 'type', 'note'],
    'accesslist': ['direction', 'source_IP', 'source_map_IP', 'source_port', 'dest_IP', 'dest_map_IP', 'dest_port',
                   'transport_protocal', 'app_protocal', 'access_use', 'vpn_domain']
}

fileNames = {
    'fengdu': 'HW封堵',
    'jiefeng': 'HW解封',
    'paicha': 'HW排查',
    'jichufd': '深圳封堵',
    'jichujf': '深圳解封',
    'iplist': 'IP名单',
    'accesslist': '网络策略开通',
}
