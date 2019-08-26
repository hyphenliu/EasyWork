from django.db import models


class Contact(models.Model):
    organization = models.CharField(max_length=50, verbose_name='公司')
    department = models.CharField(max_length=20, verbose_name='部门')
    name = models.CharField(max_length=20, verbose_name='姓名')
    address = models.CharField(max_length=20, verbose_name='办公地点exit')
    phone = models.CharField(max_length=20, verbose_name='电话')
    email = models.CharField(max_length=50, verbose_name='邮箱')  # 不用EmailField是因为抓取到数据可能就是错误的
    duty = models.CharField(max_length=10, verbose_name='职务')
    update = models.DateField(auto_now=True, verbose_name='更新日期')

    class Meta:
        ordering = ('-organization', '-department', '-duty', 'phone')
        verbose_name = '通讯录'
        verbose_name_plural = '通讯录'

    def __str__(self):
        return self.organization


class SOX(models.Model):
    '''部门控制点'''
    staff = models.CharField(max_length=100, verbose_name='部门责任人')
    stand_point = models.CharField(max_length=20, verbose_name='标准控制点编号')
    province_point = models.CharField(max_length=20, verbose_name='公司控制点编号')
    area = models.CharField(max_length=20, verbose_name='适用范围')
    procedure = models.CharField(max_length=30, verbose_name='业务流程')
    sub_procedure = models.CharField(max_length=30, verbose_name='子流程')
    control_goal = models.CharField(max_length=200, verbose_name='控制目标')
    company_describe = models.TextField(verbose_name='公司控制点描述')
    standard_describe = models.TextField(verbose_name='标准控制点描述')
    frequency = models.CharField(max_length=20, verbose_name='发生频率')
    control_type = models.CharField(max_length=20, verbose_name='控制类型')
    control_method = models.CharField(max_length=20, verbose_name='控制方式')
    department_list = models.CharField(max_length=250, verbose_name='具体部门')
    duty = models.CharField(max_length=200, verbose_name='控制点负责人')
    classification = models.CharField(max_length=5, verbose_name='控制点分类')
    reference_file = models.CharField(max_length=250, verbose_name='参考文件')
    focus_point = models.CharField(max_length=200, verbose_name='建议关注点')
    test_file = models.CharField(max_length=200, verbose_name='参考的穿行测试资料')
    update = models.DateField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        ordering = ('stand_point', 'staff')
        verbose_name = 'SOX控制矩阵'
        verbose_name_plural = 'SOX控制矩阵'
        unique_together = ('province_point','update')

    def __str__(self):
        return self.province_point
