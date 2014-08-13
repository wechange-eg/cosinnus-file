# -*- coding: utf-8 -*-
"""
Created on 10.12.2013

@author: Sascha Narr
"""
from __future__ import unicode_literals

from cosinnus.utils.renderer import BaseRenderer


class FileEntryRenderer(BaseRenderer):

    template = 'cosinnus_file/attached_files.html'
    template_single = 'cosinnus_file/single_file.html'
    
    @classmethod
    def render(cls, context, myobjs):
        files = []
        images = []
        for fileobj in myobjs:
            if fileobj.is_image:
                images.append(fileobj)
            else:
                files.append(fileobj)
        return super(FileEntryRenderer, cls).render(context, files=files, images=images, all_files=files+images)
    
