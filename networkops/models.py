from django.db import models


# Create your models here.
class Fengdu(models.Model):
    serial_number = models.CharField(max_length=12, verbose_name='编号')
    income_time = models.CharField(max_length=100, verbose_name="需求时间")
    number_time = models.CharField(max_length=100, verbose_name="编号时间")
    resource = models.CharField(max_length=100, verbose_name="需求来源")
    ip_list = models.TextField(verbose_name="处置IP地址")
    reason = models.CharField(max_length=250, null=False, verbose_name="处置原因")
    excutor = models.CharField(max_length=50, verbose_name="处置者")
    outcome = models.CharField(max_length=10, verbose_name="处置结果")
    outcome_time = models.CharField(max_length=100, verbose_name="处理时间")
    note = models.CharField(max_length=255, verbose_name="备注")
    time = models.DateTimeField(auto_now=True, verbose_name="添加时间")

    class Meta:
        ordering = ('-serial_number', '-income_time')
        verbose_name = 'HW封堵'
        verbose_name_plural = 'HW封堵数据表'

    def __str__(self):
        return self.serial_number


class Jiefeng(models.Model):
    serial_number = models.CharField(max_length=12, verbose_name='编号')
    income_time = models.DateTimeField(verbose_name="需求时间")
    resource = models.CharField(max_length=100, verbose_name="需求来源")
    ip_list = models.TextField(verbose_name="解封IP地址")
    excutor = models.CharField(max_length=50, verbose_name="解封者")
    outcome = models.CharField(max_length=10, verbose_name="解封结果")
    outcome_time = models.CharField(max_length=100, verbose_name="解封时间")
    note = models.CharField(max_length=255, verbose_name="备注")
    time = models.DateTimeField(auto_now=True, verbose_name="添加时间")

    class Meta:
        ordering = ('-serial_number',)
        verbose_name = '解封'
        verbose_name_plural = 'HW解封数据表'


class PaiCha(models.Model):
    serial_number = models.CharField(max_length=12, verbose_name='编号')
    reason = models.CharField(max_length=250, verbose_name="原因")
    ip_attack = models.TextField(verbose_name="攻击IP")
    ip_attacked = models.TextField(verbose_name="被攻击IP")
    location = models.CharField(max_length=250, verbose_name="物理位")
    means = models.CharField(max_length=250, verbose_name="攻击手段")
    guard = models.CharField(max_length=250, verbose_name="防护措施")
    result = models.CharField(max_length=250, verbose_name="排查结果")
    income_time = models.CharField(max_length=100, verbose_name="需求时间")
    resource = models.CharField(max_length=100, verbose_name="需求来源")
    time = models.DateTimeField(auto_now=True, verbose_name="添加时间")

    class Meta:
        ordering = ('-serial_number',)
        verbose_name = '排查'
        verbose_name_plural = 'HW排查数据表'


class Jichufd(models.Model):
    serial_number = models.CharField(max_length=12, verbose_name='编号')
    income_time = models.CharField(max_length=100, verbose_name="封堵时间")
    resource = models.CharField(max_length=100, verbose_name="封堵者")
    outcome = models.CharField(max_length=10, verbose_name="封堵结果")

    class Meta:
        ordering = ('-serial_number',)
        verbose_name = '深圳封堵'
        verbose_name_plural = '深圳封堵数据表'


class Jichujf(models.Model):
    serial_number = models.CharField(max_length=12, verbose_name='编号')
    income_time = models.CharField(max_length=100, verbose_name="解封时间")
    resource = models.CharField(max_length=100, verbose_name="解封者")
    outcome = models.CharField(max_length=10, verbose_name="解封结果")

    class Meta:
        ordering = ('-serial_number',)
        verbose_name = '深圳解封'
        verbose_name_plural = '深圳解封数据表'


class Baozhang(models.Model):
    reason = models.CharField(max_length=250, verbose_name="告警内容")
    ip_source = models.TextField(verbose_name="源IP")
    ip_dest = models.TextField(verbose_name="目的IP")
    income_time = models.CharField(max_length=100, verbose_name="告警时间")
    resource = models.CharField(max_length=100, verbose_name="告警来源")
    level = models.CharField(max_length=100, verbose_name="告警级别")

    class Meta:
        ordering = ('-income_time',)
        verbose_name = '深圳告警'
        verbose_name_plural = '深圳告警数据表'


class IPList(models.Model):
    ip = models.TextField(verbose_name='IP地址')
    location = models.CharField(max_length=250, verbose_name="位置")
    belong = models.CharField(max_length=250, verbose_name="归属")
    type = models.CharField(max_length=10, verbose_name="黑白名单")
    note = models.CharField(max_length=250, verbose_name="备注")

    class Meta:
        ordering = ('ip',)
        verbose_name = 'IP名单'
        verbose_name_plural = 'IP名单'


class AnsibleHost(models.Model):
    group = models.CharField(max_length=50, blank=True, default='')
    name = models.CharField(max_length=50, blank=True, default='')
    ssh_host = models.CharField(max_length=50, blank=True, default='')
    ssh_user = models.CharField(max_length=50, blank=True, default='')
    ssh_port = models.CharField(max_length=50, blank=True, default='')
    server_type = models.CharField(max_length=50, blank=True, default='')
    commit = models.TextField(blank=True, null=True)


class AccessList(models.Model):
    direction = models.CharField(max_length=120, verbose_name="访问方向")
    source_IP = models.CharField(max_length=120, verbose_name="源地址")
    source_map_IP = models.CharField(max_length=120, verbose_name="源地址对应的映射IP")
    source_port = models.CharField(max_length=120, verbose_name="源端口")
    dest_IP = models.CharField(max_length=120, verbose_name="目的地址")
    dest_map_IP = models.CharField(max_length=120, verbose_name="目的地址对应的映射IP")
    dest_port = models.CharField(max_length=120, verbose_name="目的端口")
    transport_protocal = models.CharField(max_length=120, verbose_name="传输层协议")
    app_protocal = models.CharField(max_length=120, verbose_name="应用层协议")
    access_use = models.CharField(max_length=120, verbose_name="策略用途")
    vpn_domain = models.CharField(max_length=120, verbose_name="接入IP承载网所属VPN域")
    update = models.DateField(auto_now_add=True, verbose_name="添加日期")

    class Meta:
        ordering = ('-update', 'source_IP')
        verbose_name = '网络策略'
        verbose_name_plural = '网络策略'
        unique_together=('source_IP','dest_IP','dest_port')
