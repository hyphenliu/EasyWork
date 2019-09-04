from django.urls import path

from .views import *

urlpatterns = [
    path('access_list/', access_list, name='access_list'),
    path('accesslist/', accesslist, name='accesslist'),
    path('access_list_product/', access_list_product, name='access_list_product'),
    path('devicecheck/', devicecheck, name='devicecheck'),
    path('devicecheck_ajax/', devicecheck_ajax, name='devicecheck_ajax'),
    path('paicha/', paicha, name='paicha'),
    path('paicha_ajax/', paicha_ajax, name='paicha_ajax'),
    path('fengdu/', fengdu, name='fengdu'),
    path('iplist/', ipCheck, name='ipcheck'),
    path('listpage/<tablename>/', listpage, name='listpage'),
]