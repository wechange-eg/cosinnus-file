# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


cosinnus_root_patterns = patterns('', )


cosinnus_group_patterns = patterns('cosinnus_file.views',
    #url(r'^list/$',
    #    'file_list_view',
    #    name='list'),
    url(r'^list/$',
        'file_hybrid_list_view',
        name='list'),
                                   
    url(r'^list/(?P<slug>[^/]+)/$', 'file_hybrid_list_view', name='list'),
    url(r'^(?P<slug>[^/]+)/$', 'file_update_view', name='file-update'),

    url(r'^list/(?P<tag>[^/]+)/$',
        'file_list_view',
        name='list-filtered'),

    url(r'^add/$',
        'file_create_view',
        {'form_view': 'create'},
        name='add'),

    url(r'^addfolder/$',
        'file_create_view',
        {'form_view': 'create_folder'},
        name='addfolder'),

    url(r'^(?P<slug>[^/]+)/add/$',
        'file_create_view',
        {'form_view': 'create'},
        name='add'),

    url(r'^(?P<slug>[^/]+)/addfolder/$',
        'file_create_view',
        {'form_view': 'create_folder'},
        name='addfolder'),


    url(r'^(?P<slug>[^/]+)/$',
        'file_detail_view',
        name='file'),

    url(r'^(?P<slug>[^/]+)/download$',
        'file_download_view',
        name='download'),

    url(r'^(?P<slug>[^/]+)/delete/$',
        'file_delete_view',
        {'form_view': 'delete'},
        name='delete'),

    url(r'^(?P<slug>[^/]+)/update/$',
        'file_update_view',
        {'form_view': 'update'},
        name='update'),

    url(r'^$',
        'file_index_view',
        name='index'),
)

urlpatterns = cosinnus_group_patterns + cosinnus_root_patterns
