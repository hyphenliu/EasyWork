from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(AssetsSchedual)
admin.site.register(AssetsInventory)
admin.site.register(AssetsERP)
admin.site.register(AssetsInventoried)
admin.site.register(AssetsPrescrap)
admin.site.register(AssetsScraped)
