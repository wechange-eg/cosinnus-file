# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from cosinnus_file.views import (FileCreateView, FileDeleteView,
    FileDetailView, FileIndexView, FileListView, FileUpdateView)


urlpatterns = patterns('',
    url(r'^list/$',
        FileListView.as_view(),
        name='sinn_file-entry-list'),

    url(r'^list/(?P<tag>[^/]+)/$',
        FileListView.as_view(),
        name='sinn_file-entry-list-filtered'),

    url(r'^create/$',
        FileCreateView.as_view(),
        {'form_view': 'create'},
        name='sinn_file-entry-create'),

    url(r'^entry/(?P<pk>\d+)/$',
        FileDetailView.as_view(),
        name='sinn_file-entry-detail'),

    url(r'^entry/(?P<pk>\d+)/delete/$',
        FileDeleteView.as_view(),
        {'form_view': 'delete'},
        name='sinn_file-entry-delete'),

    url(r'^entry/(?P<pk>\d+)/update/$',
        FileUpdateView.as_view(),
        {'form_view': 'update'},
        name='sinn_file-entry-update'),

    url(r'^$',
        FileIndexView.as_view(),
        name='sinn_file-entry-index'),
)
