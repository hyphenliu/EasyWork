from django.contrib import admin

# Register your models here.
from .models import *

# admin.site.register(Fengdu)
# admin.site.register(Jiefeng)
admin.site.register(Jichujf)
admin.site.register(Jichufd)
admin.site.register(PaiCha)
admin.site.register(IPList)
admin.site.register(Baozhang)


@admin.register(Fengdu)
class FengduAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'reason', 'ip_list')
    #fields = ['serial_number', 'reason', 'ip_list']

@admin.register(Jiefeng)
class JiefengAdmin(admin.ModelAdmin):
    list_display = ('serial_number','ip_list')