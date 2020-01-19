from django.urls import path

from .views import *

urlpatterns = [
    path('weekreport/', weeklyReport, name='weeklyreport'),
    path('taxilist/', taxiList, name='taxilist'),
    path('sox/', sox, name='sox'),
    path('taxi_ajax/<tablename>/', taxi_ajax, name='taxi_ajax'),
    path('sox_config/', sox_config, name='sox_config'),
    path('sox_config_ajax/', sox_config_ajax, name='sox_config_ajax'),
    path('cmitcontact/', cmitcontact, name='cmitcontact'),
    path('cmitcontact_ajax/', cmitcontact_ajax, name='cmitcontact_ajax'),
    path('cmitcontact_progress/', cmitcontact_progress, name='cmitcontact_progress'),
    path('listpage/<tablename>/', listpage, name='listpage'),
]