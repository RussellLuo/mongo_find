# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from .views import show_sites

urlpatterns = patterns('',
    url(r'^$', show_sites, {'template': 'sites/index.html'}),
)
