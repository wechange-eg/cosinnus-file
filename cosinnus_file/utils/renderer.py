# -*- coding: utf-8 -*-
"""
Created on 10.12.2013

@author: Sascha Narr
"""
from __future__ import unicode_literals

from cosinnus.utils.renderer import BaseRenderer

class FileEntryRenderer(BaseRenderer):

    template = 'cosinnus_file/attached_files.html'

    @classmethod
    def render(cls, context, myobjs):
        return super(FileEntryRenderer, cls).render(context, files=myobjs)
