# Generated by Django 2.1.7 on 2019-07-30 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dailywork', '0004_auto_20190730_1827'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ('-organization', '-department', 'phone'), 'verbose_name': '通讯录', 'verbose_name_plural': '通讯录'},
        ),
    ]
