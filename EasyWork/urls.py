"""EasyWork URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from .views import *

urlpatterns = [
    path('', index),
    path('assets/', include('inventory.urls')),
    path('admin/', admin.site.urls),
    path('network/', include('networkops.urls')),
    path('dailywork/', include('dailywork.urls')),
    path('budgets/', include('budgets.urls')),
    path('upload/<module>/<tableName>', uploadFile),
    path('download/<module>/<tableName>', downloadFile),
    path('exportexcel/<module>/<tableName>', exportExcel),
    path('downloadexcel/<module>/<tableName>', downloadExcel),
    path('exportquery/<module>/<tableName>', exportBatchQueryResult),
    path('randompasswd', randomPasswd),
    path('randompasswd_ajax', randompasswd_ajax),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += [path('accounts/', include('django.contrib.auth.urls')), ]

import EasyWork.utils.scheduler