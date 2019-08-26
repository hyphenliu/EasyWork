from django.urls import path

from .views import *

urlpatterns = [
    path('weekreport/', weeklyReport, name='weeklyreport'),
    path('taxilist/', taxiList, name='taxilist'),
    path('sox/', sox, name='sox'),
    path('taxi_ajax/<tablename>/', taxi_ajax, name='taxi_ajax'),
    path('sox_ajax/<tablename>/', sox_ajax, name='sox_ajax'),
    path('cmitcontact/', cmitcontact, name='cmitcontact'),
    path('cmitcontact_ajax/', cmitcontact_ajax, name='cmitcontact_ajax'),
    path('listpage/<tablename>/', listpage, name='listpage'),
]