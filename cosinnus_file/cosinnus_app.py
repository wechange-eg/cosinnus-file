# -*- coding: utf-8 -*-

from cosinnus_file.templatetags import renderer

IS_COSINNUS_APP = True
COSINNUS_APP_NAME = 'file'

ATTACHABLE_OBJECT_MODELS = ['FileEntry']
ATTACHABLE_OBJECT_RENDERERS = {'FileEntry':renderer.FileEntryRenderer}