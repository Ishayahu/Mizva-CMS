# -*- coding:utf-8 -*-
# coding=<utf8>

from django.conf.urls.defaults import patterns, include, url
import todoes.views 
#import assets.views
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    # просмотр задач
    url(r'^/$', todoes.views.clients),
   url(r'^$', todoes.views.clients),
    # просмотр всех задач
    url(r'^all_clients/$', todoes.views.all_clients),
    url(r'^new_client/$', todoes.views.new_client),
    url(r'^edit/([^/]+)/$', todoes.views.edit_client),
    # клиент и заказы
    url(r'^client/(\d+)/$', todoes.views.client),
    url(r'^client_claims/(\d+)/$', todoes.views.client_claims),
    url(r'^print/payment/(\d+)/$', todoes.views.print_payment),
    url(r'^edit_payment/(\d+)/$', todoes.views.edit_payment),
    url(r'^debt/(\d+)/(\d+)/$', todoes.views.debt),

    # установка напоминалки повторяющейся задачи
    # удаление повторяющейся задачи
    url(r'^deleted_tasks/$', todoes.views.deleted_tasks),
    url(r'^delete/([^/]+)/(\d+)/$', todoes.views.delete_task),
    url(r'^completle_delete/([^/]+)/(\d+)/$', todoes.views.completle_delete_task),
    url(r'^undelete/([^/]+)/(\d+)/$', todoes.views.undelete_task),
    url(r'^add_children_task/([^/]+)/(\d+)/$', todoes.views.add_children_task),
    # http://192.168.1.157:8080/move_to_call/47 - изменение категории на "Звонки"
    url(r'^move_to_call/([^/]+)/(\d+)/$', todoes.views.move_to_call),
    # http://192.168.1.157:8080/set_reminder/47 - установка напоминания для задачи
    url(r'^set_reminder/([^/]+)/(\d+)/$', todoes.views.set_reminder), 
    # Для администратора:
    url(r'^users/', todoes.views.get_all_logged_in_users),
    url(r'^accounts/$', login),
    url(r'^accounts/login/$', login),
    url(r'^accounts/register/$', todoes.views.register),
    url(r'^accounts/logout/$', logout),
    url(r'^accounts/profile/$', todoes.views.profile),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

# Работа с активами
    # Добавление актива
    #url(r'^assets/add/([^/]+)/$', assets.views.asset_add),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
