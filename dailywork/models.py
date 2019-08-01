from django.db import models


class Contact(models.Model):
    organization = models.CharField(max_length=50, verbose_name='公司')
    department = models.CharField(max_length=20, verbose_name='部门')
    name = models.CharField(max_length=20, verbose_name='姓名')
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
