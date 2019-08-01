from django.urls import path

from .views import *

urlpatterns = [
    path('accesslist/', accesslist, name='accesslist'),
    path('accesslist_product/', accesslist_product, name='accesslist_product'),
    path('devicecheck/', devicecheck, name='devicecheck'),
    path('devicecheck_ajax/', devicecheck_ajax, name='devicecheck_ajax'),
    path('paicha/', paicha, name='paicha'),
    path('paicha_ajax/', paicha_ajax, name='paicha_ajax'),
    path('fengdu/', fengdu, name='fengdu'),
    path('iplist/', ipCheck, name='ipcheck'),
    path('listpage/<tablename>/', listpage, name='listpage'),
]