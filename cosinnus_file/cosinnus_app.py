# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cosinnus_file.utils import renderer

IS_COSINNUS_APP = True
COSINNUS_APP_NAME = 'file'
COSINNUS_APP_LABEL = _('Files')


ATTACHABLE_OBJECT_MODELS = ['cosinnus_file.FileEntry']
ATTACHABLE_OBJECT_RENDERERS = {'cosinnus_file.FileEntry': renderer.FileEntryRenderer}
