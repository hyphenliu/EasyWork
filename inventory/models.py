from django.db import models


class AssetsERP(models.Model):
    asset_code = models.CharField('资产编码', max_length=10, null=False)
    asset_label = models.CharField('资产标签', max_length=12)
    asset_name = models.TextField('资产名称', null=False)
    asset_type = models.CharField('资产类别', max_length=50)
    type_describe = models.TextField('资产类别描述', max_length=250)
    serial_number = models.CharField('资产序列号', max_length=150)
    keyword = models.CharField('资产关键字', max_length=150)
    manufactor = models.CharField('厂商', max_length=150)
    model = models.CharField('规格型号', max_length=150)
    number = models.IntegerField('数量', null=False)
    unit_type = models.CharField('单位', max_length=10)
    import_date = models.DateField('创建日期', null=False)
    use_date = models.DateField('启用日期', null=False)
    depreciate_date = models.DateField('按比例分摊日期', null=False)
    depreciate_method = models.CharField('折旧方法', max_length=150, null=False)
    limit_year = models.IntegerField('使用年限', null=False)
    remainder_month = models.IntegerField('剩余月数', null=False)
    cost = models.FloatField('成本', null=False)
    remainder_value = models.FloatField('资产净值', null=False)
    remainder_count = models.FloatField('资产净额', null=False)
    residual_value = models.FloatField('残值', null=False)
    month_depreciate = models.FloatField('本期折旧额', null=False)
    year_depreciate = models.FloatField('本年折旧额', null=False)
    accumulate_depreciate = models.FloatField('累计折旧额', null=False)
    month_diminution = models.FloatField('本期减值准备')
    year_diminution = models.FloatField('本年减值准备')
    accumulate_diminution = models.FloatField('累计减值准备')
    staff_code = models.CharField('员工编号', max_length=10, null=False)
    staff_name = models.CharField('员工姓名', max_length=10, null=False)
    address = models.CharField('地点', max_length=250, null=False)
    address_describe = models.CharField('地点说明', max_length=250)
    early_code = models.CharField('期初资产卡片编号', max_length=10)
    early_label = models.CharField('期初资产标签编号', max_length=12)
    early_project_id = models.CharField('期初估列项目编号', max_length=50)
    project_status = models.CharField('建设状态', max_length=20)
    project_source = models.CharField('资产来源', max_length=150)
    project_id = models.CharField('项目编号', max_length=50)
    project_name = models.CharField('项目名称', max_length=150)
    other_attachment = models.CharField('其他附加信息', max_length=150)
    bounch7 = models.CharField('弹性域信息7', max_length=150)
    bounch8 = models.CharField('弹性域信息8', max_length=150)
    bounch9 = models.CharField('弹性域信息9', max_length=150)
    bounch10 = models.CharField('弹性域信息10', max_length=150)
    cost_account = models.CharField('成本帐户', max_length=150)
    cost_account_describe = models.CharField('成本帐户描述', max_length=250)
    depreciate_account = models.CharField('折旧帐户', max_length=150)
    depreciate_account_describe = models.CharField('折旧帐户描述', max_length=250)
    accumulate_account = models.CharField('累计折旧帐户', max_length=150)
    accumulate_account_describe = models.CharField('累计折旧帐户描述', max_length=250)
    budgets_company = models.CharField('预算公司段', max_length=150)
    budgets_department = models.CharField('预算责任部门', max_length=150)
    budgets_project = models.CharField('预算项目', max_length=150)
    budgets_service = models.CharField('预算业务活动', max_length=150)
    budgets_subject = models.CharField('预算科目', max_length=150)
    service_platform = models.CharField('业务平台', max_length=150)
    network_level = models.CharField('网络层次', max_length=150)
    coconstruct = models.CharField('是否共建', max_length=5)
    budgets_contract = models.CharField('预算合同信息', max_length=250)
    actual_number = models.CharField('实际数量', max_length=250)
    deduction_label = models.CharField('资产抵扣标识', max_length=150)
    finacial_type = models.CharField('财产类型', max_length=50)
    scrap_date = models.DateField('可报废日期', null=True)

    class Meta:
        ordering = ['asset_label']
        verbose_name = 'ERP原始数据表'
        verbose_name_plural = 'ERP原始数据表'

class AssetsSchedual(models.Model):
    asset_label = models.CharField('资产标签', max_length=12, unique=True)
    asset_name = models.TextField('资产名称', null=False)
    model = models.CharField('规格型号', max_length=150)
    manufactor = models.CharField('制造商', max_length=150)
    address = models.CharField('位置', null=False, max_length=250)
    staff_department = models.CharField('责任部门', max_length=10, null=False)
    staff_name = models.CharField('责任人', max_length=10, null=False)
    note = models.CharField('备注', max_length=250)
    schedual_date = models.DateField('计划盘点时间', auto_now=True)

    class Meta:
        ordering = ['asset_label']
        verbose_name = '盘点清册'
        verbose_name_plural = '盘点清册'


class AssetsInventoried(models.Model):
    asset_label = models.CharField('资产标签', max_length=12)
    asset_name = models.TextField('资产名称', null=False)
    model = models.CharField('规格型号', max_length=150)
    manufactor = models.CharField('制造商', max_length=150)
    address = models.CharField('位置', null=False, max_length=250)
    staff_department = models.CharField('责任部门', max_length=10, null=False)
    staff_name = models.CharField('责任人', max_length=10, null=False)
    note = models.CharField('备注', max_length=250)
    schedual_date = models.DateField('盘点时间', auto_now=True)

    class Meta:
        ordering = ['asset_label']
        verbose_name = '盘点清册'
        verbose_name_plural = '盘点清册'


class AssetsInventory(models.Model):
    machine_address = models.CharField('资产地理位置', max_length=150)
    machine_room = models.CharField('资产机房', max_length=150)
    machine_column = models.CharField('资产机架', max_length=150)
    machine_racket = models.CharField('资产机柜', max_length=150)
    asset_label = models.CharField('资产标签', max_length=12)
    asset_name = models.TextField('资产名称')
    model = models.CharField('规格型号', max_length=150)
    manufactor = models.CharField('制造商', max_length=150)
    staff_name = models.CharField('责任人', max_length=10, null=True)
    note = models.CharField('备注', max_length=250)
    inventory_date = models.DateField('盘点时间', auto_now=True)

    class Meta:
        ordering = ['machine_address', 'machine_room', 'machine_column', 'machine_racket']
        verbose_name = '盘点结果'
        verbose_name_plural = '盘点结果'


class AssetsPrescrap(models.Model):
    '''
    拟报废资产表
    '''
    asset_label = models.CharField('资产标签', max_length=12)
    asset_name = models.TextField('资产名称')
    model = models.CharField('规格型号', max_length=150)
    staff_name = models.CharField('责任人', max_length=10, null=False)
    address = models.CharField('位置', max_length=250, null=False)
    noservice = models.BooleanField('业务上不再使用')
    nopower = models.BooleanField('下电')
    need_erase = models.BooleanField('设备消磁')
    cable_extract = models.BooleanField('连接线拆除')
    can_move = models.BooleanField('达到可以搬离状态')
    prescraped_label = models.BooleanField('已进行拟报废标示')
    cost = models.FloatField('成本', null=False)
    use_date = models.DateField('启用日期', null=False)
    remainder_month = models.IntegerField('剩余月数', null=False)
    remainder_value = models.FloatField('资产净额', null=False)
    note = models.CharField('备注', max_length=250)
    prescraped_date = models.DateField('拟报废时间', auto_now=True)

    class Meta:
        ordering = ['asset_label']
        verbose_name = '拟报废清单'
        verbose_name_plural = '拟报废清单'


class AssetsScraped(models.Model):
    asset_label = models.CharField('资产标签号', max_length=12, unique=True)
    asset_name = models.TextField('设备名称')
    model = models.CharField('规格', max_length=150)
    manufactor = models.CharField('制造商', max_length=150, null=True)
    staff_department = models.CharField('管理部门', max_length=10, null=True)
    staff_name = models.CharField('责任人', max_length=10, null=True)

    class Meta:
        ordering = ['asset_label']
        verbose_name = '已报废清单'
        verbose_name_plural = '已报废清单'
