# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from cosinnus_file.views import (FileCreateView, FileDeleteView,
    FileDetailView, FileIndexView, FileListView, FileUpdateView)


urlpatterns = patterns('',
    url(r'^list/$',
        FileListView.as_view(),
        name='list'),

    url(r'^list/(?P<tag>[^/]+)/$',
        FileListView.as_view(),
        name='list-filtered'),

    url(r'^add/$',
        FileCreateView.as_view(),
        {'form_view': 'create'},
        name='add'),

    url(r'^(?P<slug>[^/]+)/$',
        FileDetailView.as_view(),
        name='file'),

    url(r'^(?P<slug>[^/]+)/delete/$',
        FileDeleteView.as_view(),
        {'form_view': 'delete'},
        name='delete'),

    url(r'^(?P<slug>[^/]+)/update/$',
        FileUpdateView.as_view(),
        {'form_view': 'update'},
        name='update'),

    url(r'^$',
        FileIndexView.as_view(),
        name='index'),
)
