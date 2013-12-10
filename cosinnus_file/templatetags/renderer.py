# -*- coding: utf-8 -*-
"""
Created on 10.12.2013

@author: Sascha Narr
"""
from __future__ import unicode_literals

from django.template.loader import render_to_string


class FileEntryRenderer(object):

    def __init__(self, params):
        pass

    @staticmethod
    def render_attached_objects(context, files):
        template="cosinnus_file/attached_file_template.html"
        
        #if not 'request' in context:
        #    raise ImproperlyConfigured("Current request missing in rendering "
        #        "context. Include 'django.core.context_processors.request' in the "
        #        "TEMPLATE_CONTEXT_PROCESSORS.")
        
        context[files] = files
        
        return render_to_string(template, context)