"""tinydb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from myadmin.views import index, users,tests

urlpatterns = [
    # 后台首页
    url(r'^$', index.index, name='myadmin_index'),

    # 后台用户管理
    url(r'^users$', users.index, name="myadmin_users_index"),
    url(r'^users/add$', users.add, name="myadmin_users_add"),
    url(r'^users/insert$', users.insert, name="myadmin_users_insert"),
    url(r'^users/del/(?P<uid>[0-9]+)$', users.delete, name="myadmin_users_del"),
    url(r'^users/edit/(?P<uid>[0-9]+)$', users.edit, name="myadmin_users_edit"),
    url(r'^users/update/(?P<uid>[0-9]+)$', users.update, name="myadmin_users_update"),

    # 后台题目管理
    url(r'^tests$', tests.index, name="myadmin_tests_index"),
    url(r'^tests/add$', tests.add, name="myadmin_tests_add"),
    url(r'^tests/insert$', tests.insert, name="myadmin_tests_insert"),
    url(r'^tests/del/(?P<uid>[0-9]+)$', tests.delete, name="myadmin_tests_del"),
    url(r'^tests/edit/(?P<uid>[0-9]+)$', tests.edit, name="myadmin_tests_edit"),
    url(r'^tests/update/(?P<uid>[0-9]+)$', tests.update, name="myadmin_tests_update"),


    # 后台管理员路由
    url(r'^login$', index.login, name="myadmin_login"),
    url(r'^dologin$', index.dologin, name="myadmin_dologin"),
    url(r'^logout$', index.logout, name="myadmin_logout"),
]
