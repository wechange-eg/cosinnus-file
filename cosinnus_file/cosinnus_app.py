# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def register():
    # Import here to prevent import side effects
    from django.utils.translation import ugettext_lazy as _

    from cosinnus.core.registries import (app_registry,
        attached_object_registry, url_registry, widget_registry)

    app_registry.register('cosinnus_file', 'file', _('Files'))
    attached_object_registry.register('cosinnus_file.FileEntry',
                             'cosinnus_file.utils.renderer.FileEntryRenderer')
    url_registry.register_urlconf('cosinnus_file', 'cosinnus_file.urls')
    widget_registry.register('file', 'cosinnus_file.dashboard.Latest')
