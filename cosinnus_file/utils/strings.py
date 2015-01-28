# -*- coding: utf-8 -*-
"""
Created on 10.12.2013

@author: Sascha Narr
"""
from __future__ import unicode_literals

import urllib

def clean_filename(name):
    return urllib.quote(name.encode('utf-8', 'ignore')).replace('%28', '(').replace('%29', ')')\
        .replace('%21', '!').replace('%27', "'")