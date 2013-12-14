# -*- coding: utf-8 -*-

from cosinnus_file.utils import renderer

IS_COSINNUS_APP = True
COSINNUS_APP_NAME = 'file'

ATTACHABLE_OBJECT_MODELS = ['cosinnus_file.FileEntry']
ATTACHABLE_OBJECT_RENDERERS = {'cosinnus_file.FileEntry': renderer.FileEntryRenderer}
