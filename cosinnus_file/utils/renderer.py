# -*- coding: utf-8 -*-
"""
Created on 10.12.2013

@author: Sascha Narr
"""
from __future__ import unicode_literals

from django.template.loader import render_to_string


class FileEntryRenderer(object):

    @staticmethod
    def render_attached_objects(context, files, template="cosinnus_file/attached_files.html"):
        context['files'] = files
        return render_to_string(template, context)