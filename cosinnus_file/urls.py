# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url


cosinnus_root_patterns = patterns('', )


cosinnus_group_patterns = patterns('cosinnus_file.views',
    #url(r'^list/$',
    #    'file_list_view',
    #    name='list'),
    url(r'^list/$', 'file_hybrid_list_view', name='list'),
    url(r'^list/download/$', 'folder_download_view', name='download-folder'),
    url(r'^list/move_element/$', 'move_element_view', name='move-element'),
    url(r'^list/(?P<slug>[^/]+)/$', 'file_hybrid_list_view', name='list'),
    url(r'^list/(?P<slug>[^/]+)/download/$', 'folder_download_view', name='download-folder'),
    url(r'^upload_inline/$', 'file_upload_inline', name='upload-inline'),
    url(r'^(?P<slug>[^/]+)/$', 'file_update_view', name='edit'),

    #url(r'^list/(?P<tag>[^/]+)/$', 'file_list_view', name='list-filtered'),
    #url(r'^(?P<slug>[^/]+)/$', 'file_detail_view', name='file'),
    url(r'^(?P<slug>[^/]+)/download$', 'file_download_view', name='download'),
    url(r'^(?P<slug>[^/]+)/save', 'file_download_view', {'force_download': True}, name='save'),
    url(r'^(?P<slug>[^/]+)/delete/$', 'file_delete_view', {'form_view': 'delete'}, name='delete'),
    
    url(r'^$', 'file_index_view', name='index'),
)

urlpatterns = cosinnus_group_patterns + cosinnus_root_patterns
