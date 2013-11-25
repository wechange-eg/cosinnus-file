# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from cosinnus_file.models import FileEntry


NOTIFY_MODELS = [FileEntry]
NOTIFY_POST_SUBSCRIBE_URLS = {
    'file.FileEntry': {
        'show': lambda obj, group: obj.get_absolute_url(),
        'list': lambda obj, group: reverse('cosinnus:file:list', kwargs={'group': group.name}),
    },
}
