from django.urls import path

from .views import *

urlpatterns = [
    path('erp/', erp, name='assetsIndex'),
    path('erpsoft/', erp, name='assetsIndex'),
    path('inventory/', inventory, name='inventory'),
    path('inventoried/', inventoried, name='inventoried'),
    path('schedual/', schedual, name='schedual'),
    path('prescrap/', prescrap, name='prescrap'),
    path('scraped/', scraped, name='scraped'),
    path('scrap/', scrap, name='scrap'),
    path('statistic/', statistic, name='statistic'),
    path('dataimport/', dataimport, name='dataimport'),
    path('listpage/<tablename>/', listpage, name='listpage'),
    path('inventoring/', inventoring, name='inventoring'),
    path('updateErp/', updateErp, name='updateErp')

]