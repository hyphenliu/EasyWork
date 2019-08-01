from inventory.models import *

# 数据库表
tableClass = {'erp': AssetsERP, 'schedual': AssetsSchedual, 'inventoried': AssetsInventoried,
              'inventory': AssetsInventory, 'prescrap': AssetsPrescrap, 'scraped': AssetsScraped}
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
    'scraped': ['asset_label', 'asset_name', 'model', 'manufactor', 'staff_department', 'staff_name']
}

tableTitles = {
    'erp': ['资产编号', '资产标签号', '资产名称', '资产类别', '资产类别描述', '序列号', '资产关键字', '厂商', '规格型号', '数量', '单位', '创建日期', '启用日期',
            '按比例分摊日期', '折旧方法', '使用年限', '剩余月数', '成本', '资产净值', '资产净额', '残值', '本期折旧额', '本年折旧额', '累计折旧额', '本期减值准备',
            '本年减值准备', '累计减值准备', '员工编号', '员工姓名', '地点', '地点说明', '期初资产卡片编号', '期初资产标签编号', '期初估列项目编号', '建设状态', '资产来源',
            '项目编号', '项目名称', '其他附加信息', '弹性域信息7', '弹性域信息8', '弹性域信息9', '弹性域信息10', '成本帐户', '成本帐户描述', '折旧帐户', '折旧帐户描述',
            '累计折旧帐户', '累计折旧帐户描述', '预算公司段', '预算责任部门', '预算项目', '预算业务活动', '预算科目', '业务平台', '网络层次', '是否共建', '预算合同信息', '实际数量',
            '资产抵扣标识', '财产类型'],
    'schedual': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventoried': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventory': ['机房地点', '机房位置', '机架列', '机架号', '资产编码', '设备名称', '规格', '制造商', '责任人',  '备注'],
    'prescrap': ['资产标签号', '资产名称', '规格型号', '责任人', '位置', '业务上不能再使用', '下电', '设备消磁', '连接线拆除', '达到可以搬离状态', '已进行拟报废标示', '原值',
                 '启用日期', '折旧剩余月数', '资产净额', '备注'],
    'scraped': ['资产标签号', '设备名称', '规格', '制造商', '管理部门', '责任人']
}

htmlTitles = {
    'erp': ['资产标签号', '资产名称', '厂商', '规格型号', '创建日期', '启用日期', '使用年限', '剩余月数', '成本','资产净额', '员工编号', '员工姓名', '地点', '期初资产标签编号',
            '项目编号', '项目名称', '其他附加信息'],
    'schedual': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventoried': ['设备编码', '设备名称', '规格', '制造商', '位置', '责任部门', '责任人', '备注'],
    'inventory': ['机房地点', '机房位置', '机架列', '机架号', '资产编码', '设备名称', '规格', '制造商', '责任人',  '备注'],
    'prescrap': ['资产标签号', '资产名称', '规格型号', '责任人', '位置', '业务上不能再使用', '下电', '设备消磁', '连接线拆除', '达到可以搬离状态', '已进行拟报废标示', '原值',
                 '启用日期', '折旧剩余月数', '资产净额', '备注'],
    'scraped': ['资产标签号', '设备名称', '规格', '制造商', '管理部门', '责任人']
}

htmlColums = {
    'erp': ['asset_label', 'asset_name', 'manufactor', 'model', 'import_date', 'use_date', 'limit_year',
            'remainder_month', 'cost', 'remainder_count','staff_code', 'staff_name', 'address', 'early_label', 'project_id',
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
    'scraped': ['asset_label', 'asset_name', 'model', 'manufactor', 'staff_department', 'staff_name']
}

fileNames = {
    'erp': '资产明细',
    'schedual': '盘点清册',
    'inventory': '盘点结果',
    'prescrap': '拟报废清单',
    'scraped': '已报废清单',
}
